# account
from nomad_media_pip.common.account_authentication.login import _login
from nomad_media_pip.common.account_authentication.refresh_token import _refresh_token

# admin
from nomad_media_pip.admin.asset_upload.cancel_upload import _cancel_upload
from nomad_media_pip.admin.asset_upload.multi_thread_upload import  _multi_thread_upload
from nomad_media_pip.admin.asset_upload.start_asset_upload import _start_upload
from nomad_media_pip.admin.asset_upload.start_related_asset_upload import _start_related_asset_upload
from nomad_media_pip.admin.asset_upload.upload_complete_asset import _upload_complete_asset

from nomad_media_pip.admin.audit.get_audit import _get_audit

from nomad_media_pip.admin.config.clear_server_cache import _clear_server_cache
from nomad_media_pip.admin.config.get_config import _get_config
from nomad_media_pip.admin.config.get_server_time import _get_server_time

from nomad_media_pip.admin.content.create_content import _create_content
from nomad_media_pip.admin.content.deactivate_content_user_track import _deactivate_content_user_track
from nomad_media_pip.admin.content.delete_content import _delete_content
from nomad_media_pip.admin.content.get_content import _get_content
from nomad_media_pip.admin.content.get_content_user_track import _get_content_user_track
from nomad_media_pip.admin.content.get_content_user_track_touch import _get_content_user_track_touch
from nomad_media_pip.admin.content.update_content import _update_content

from nomad_media_pip.admin.event.add_live_schedule_to_event import _add_live_schedule_to_event
from nomad_media_pip.admin.event.create_update_event import _create_and_update_event
from nomad_media_pip.admin.event.delete_event import _delete_event
from nomad_media_pip.admin.event.extend_live_schedule import _extend_live_schedule
from nomad_media_pip.admin.event.get_live_schedule import _get_live_schedule
from nomad_media_pip.admin.event.start_live_schedule import _start_live_schedule
from nomad_media_pip.admin.event.stop_live_schedule import _stop_live_schedule

from nomad_media_pip.admin.live_channel.clip_live_channel import _clip_live_channel
from nomad_media_pip.admin.live_channel.create_live_channel import _create_live_channel
from nomad_media_pip.admin.live_channel.delete_live_channel import _delete_live_channel
from nomad_media_pip.admin.live_channel.get_live_channel import _get_live_channel
from nomad_media_pip.admin.live_channel.get_live_channels import _get_live_channels
from nomad_media_pip.admin.live_channel.live_channel_refresh import _live_channel_refresh
from nomad_media_pip.admin.live_channel.next_event import _next_event
from nomad_media_pip.admin.live_channel.start_live_channel import _start_live_channel
from nomad_media_pip.admin.live_channel.start_output_tracking import _start_output_tracking
from nomad_media_pip.admin.live_channel.stop_live_channel import _stop_live_channel
from nomad_media_pip.admin.live_channel.update_live_channel import _update_live_channel

from nomad_media_pip.admin.live_input.create_live_input import _create_live_input
from nomad_media_pip.admin.live_input.delete_live_input import _delete_live_input
from nomad_media_pip.admin.live_input.get_live_input import _get_live_input
from nomad_media_pip.admin.live_input.get_live_inputs import _get_live_inputs
from nomad_media_pip.admin.live_input.update_live_input import _update_live_input

from nomad_media_pip.admin.live_operator.cancel_broadcast import _cancel_broadcast
from nomad_media_pip.admin.live_operator.cancel_segment import _cancel_segment
from nomad_media_pip.admin.live_operator.complete_segment import _complete_segment
from nomad_media_pip.admin.live_operator.get_completed_segments import _get_completed_segments
from nomad_media_pip.admin.live_operator.get_live_operator import _get_live_operator
from nomad_media_pip.admin.live_operator.get_live_operators import _get_live_operators
from nomad_media_pip.admin.live_operator.start_broadcast import _start_broadcast
from nomad_media_pip.admin.live_operator.start_segment import _start_segment
from nomad_media_pip.admin.live_operator.stop_broadcast import _stop_broadcast

from nomad_media_pip.admin.live_output_profile.create_live_output_profile import _create_live_output_profile
from nomad_media_pip.admin.live_output_profile.delete_live_output_profile import _delete_live_output_profile
from nomad_media_pip.admin.live_output_profile.get_live_output_profile import _get_live_output_profile
from nomad_media_pip.admin.live_output_profile.get_live_output_profiles import _get_live_output_profiles
from nomad_media_pip.admin.live_output_profile.get_live_output_types import _get_live_output_types
from nomad_media_pip.admin.live_output_profile.update_live_output_profile import _update_live_output_profile

from nomad_media_pip.admin.live_output_profile_group.create_live_output_profile_group import _create_live_output_profile_group
from nomad_media_pip.admin.live_output_profile_group.delete_live_output_profile_group import _delete_live_output_profile_group
from nomad_media_pip.admin.live_output_profile_group.get_live_output_profile_group import _get_live_output_profile_group
from nomad_media_pip.admin.live_output_profile_group.get_live_output_profile_groups import _get_live_output_profile_groups
from nomad_media_pip.admin.live_output_profile_group.update_live_output_profile_group import _update_live_output_profile_group

from nomad_media_pip.admin.schedule_event.add_asset_schedule_event import _add_asset_schedule_event
from nomad_media_pip.admin.schedule_event.add_input_schedule_event import _add_input_schedule_event
from nomad_media_pip.admin.schedule_event.get_asset_schedule_event import _get_asset_schedule_event
from nomad_media_pip.admin.schedule_event.get_input_schedule_event import _get_input_schedule_event
from nomad_media_pip.admin.schedule_event.move_schedule_event import _move_schedule_event
from nomad_media_pip.admin.schedule_event.remove_asset_schedule_event import _remove_asset_schedule_event
from nomad_media_pip.admin.schedule_event.remove_input_schedule_event import _remove_input_schedule_event
from nomad_media_pip.admin.schedule_event.update_asset_schedule_event import _update_asset_schedule_event
from nomad_media_pip.admin.schedule_event.update_input_schedule_event import _update_input_schedule_event

from nomad_media_pip.admin.schedule.create_intelligent_playlist import _create_intelligent_playlist
from nomad_media_pip.admin.schedule.create_intelligent_schedule import _create_intelligent_schedule
from nomad_media_pip.admin.schedule.create_playlist import _create_playlist
from nomad_media_pip.admin.schedule.create_playlist_video import _create_playlist_video
from nomad_media_pip.admin.schedule.create_schedule_items.create_schedule_item_asset import _create_schedule_item_asset
from nomad_media_pip.admin.schedule.create_schedule_items.create_schedule_item_live_channel import _create_schedule_item_live_channel
from nomad_media_pip.admin.schedule.create_schedule_items.create_schedule_item_playlist_schedule import _create_schedule_item_playlist_schedule
from nomad_media_pip.admin.schedule.create_schedule_items.create_schedule_item_search_filter import _create_schedule_item_search_filter
from nomad_media_pip.admin.schedule.delete_intelligent_playlist import _delete_intelligent_playlist
from nomad_media_pip.admin.schedule.delete_intelligent_schedule import _delete_intelligent_schedule
from nomad_media_pip.admin.schedule.delete_playlist import _delete_playlist
from nomad_media_pip.admin.schedule.delete_schedule_item import _delete_schedule_item
from nomad_media_pip.admin.schedule.get_intelligent_playlist import _get_intelligent_playlist
from nomad_media_pip.admin.schedule.get_intelligent_schedule import _get_intelligent_schedule
from nomad_media_pip.admin.schedule.get_playlist import _get_playlist
from nomad_media_pip.admin.schedule.get_schedule_item import _get_schedule_item
from nomad_media_pip.admin.schedule.get_schedule_items import _get_schedule_items
from nomad_media_pip.admin.schedule.get_schedule_preview import _get_schedule_preview
from nomad_media_pip.admin.schedule.move_schedule_item import _move_schedule_item
from nomad_media_pip.admin.schedule.publish_intelligent_schedule import _publish_intelligent_schedule
from nomad_media_pip.admin.schedule.start_schedule import _start_schedule
from nomad_media_pip.admin.schedule.stop_schedule import _stop_schedule
from nomad_media_pip.admin.schedule.update_intelligent_playlist import _update_intelligent_playlist
from nomad_media_pip.admin.schedule.update_intelligent_schedule import _update_intelligent_schedule
from nomad_media_pip.admin.schedule.update_playlist import _update_playlist
from nomad_media_pip.admin.schedule.update_playlist_video import _update_playlist_video
from nomad_media_pip.admin.schedule.update_schedule_items.update_schedule_item_asset import _update_schedule_item_asset
from nomad_media_pip.admin.schedule.update_schedule_items.update_schedule_item_live_channel import _update_schedule_item_live_channel
from nomad_media_pip.admin.schedule.update_schedule_items.update_schedule_item_playlist_schedule import _update_schedule_item_playlist_schedule
from nomad_media_pip.admin.schedule.update_schedule_items.update_schedule_item_search_filter import _update_schedule_item_search_filter

from nomad_media_pip.admin.user.delete_user import _delete_user
from nomad_media_pip.admin.user.delete_user_content_attribute_data import _delete_user_content_attribute_data
from nomad_media_pip.admin.user.delete_user_content_group_data import _delete_user_content_group_data
from nomad_media_pip.admin.user.delete_user_content_security_data import _delete_user_content_security_data
from nomad_media_pip.admin.user.delete_user_data import _delete_user_data
from nomad_media_pip.admin.user.delete_user_dislike_data import _delete_user_dislike_data
from nomad_media_pip.admin.user.delete_user_favorites_data import _delete_user_favorites_data
from nomad_media_pip.admin.user.delete_user_likes_data import _delete_user_likes_data
from nomad_media_pip.admin.user.delete_user_saved_search_data import _delete_user_saved_search_data
from nomad_media_pip.admin.user.delete_user_session_data import _delete_user_session_data
from nomad_media_pip.admin.user.delete_user_video_tracking_data import _delete_user_video_tracking_data

from nomad_media_pip.admin.user_session.change_session_status import _change_session_status
from nomad_media_pip.admin.user_session.get_user_session import _get_user_session

from nomad_media_pip.common.account_authentication.forgot_password import _forgot_password
from nomad_media_pip.common.account_authentication.reset_password import _reset_password
from nomad_media_pip.common.account_authentication.logout import _logout

from nomad_media_pip.common.account_registration.register import _register
from nomad_media_pip.common.account_registration.resend_code import _resend_code
from nomad_media_pip.common.account_registration.verify import _verify

from nomad_media_pip.common.asset.archive_asset import _archive_asset
from nomad_media_pip.common.asset.build_media import _build_media
from nomad_media_pip.common.asset.clip_asset import _clip_asset
from nomad_media_pip.common.asset.copy_asset import _copy_asset
from nomad_media_pip.common.asset.create_annotation import _create_annotation
from nomad_media_pip.common.asset.create_asset_ad_break import _create_asset_ad_break
from nomad_media_pip.common.asset.create_folder_asset import _create_folder_asset
from nomad_media_pip.common.asset.create_placeholder_asset import _create_placeholder_asset
from nomad_media_pip.common.asset.create_screenshot_at_timecode import _create_screenshot_at_timecode
from nomad_media_pip.common.asset.delete_annotation import _delete_annotation
from nomad_media_pip.common.asset.delete_asset import _delete_asset
from nomad_media_pip.common.asset.delete_asset_ad_break import _delete_asset_ad_break
from nomad_media_pip.common.asset.download_archive_asset import _download_archive_asset
from nomad_media_pip.common.asset.duplicate_asset import _duplicate_asset
from nomad_media_pip.common.asset.get_annotations import _get_annotations
from nomad_media_pip.common.asset.get_asset import _get_asset
from nomad_media_pip.common.asset.get_asset_ad_breaks import _get_asset_ad_breaks
from nomad_media_pip.common.asset.get_asset_child_nodes import _get_asset_child_nodes
from nomad_media_pip.common.asset.get_asset_details import _get_asset_details
from nomad_media_pip.common.asset.get_asset_manifest_with_cookies import _get_asset_manifest_with_cookies
from nomad_media_pip.common.asset.get_asset_metadata_summary import _get_asset_metadata_summary
from nomad_media_pip.common.asset.get_asset_parent_folders import _get_asset_parent_folders
from nomad_media_pip.common.asset.get_asset_screenshot_details import _get_asset_screenshot_details
from nomad_media_pip.common.asset.get_asset_segment_details import _get_asset_segment_details
from nomad_media_pip.common.asset.get_user_upload_parts import _get_user_upload_parts
from nomad_media_pip.common.asset.get_user_uploads import _get_user_uploads
from nomad_media_pip.common.asset.import_annotations import _import_annotations
from nomad_media_pip.common.asset.index_asset import _index_asset
from nomad_media_pip.common.asset.local_restore_asset import _local_restore_asset
from nomad_media_pip.common.asset.move_asset import _move_asset
from nomad_media_pip.common.asset.records_asset_tracking_beacon import _records_asset_tracking_beacon
from nomad_media_pip.common.asset.register_asset import _register_asset
from nomad_media_pip.common.asset.reprocess_asset import _reprocess_asset
from nomad_media_pip.common.asset.restore_asset import _restore_asset
from nomad_media_pip.common.asset.share_asset import _share_asset
from nomad_media_pip.common.asset.start_workflow import _start_workflow
from nomad_media_pip.common.asset.transcribe_asset import _transcribe_asset
from nomad_media_pip.common.asset.update_annotation import _update_annotation
from nomad_media_pip.common.asset.update_asset import _update_asset
from nomad_media_pip.common.asset.update_asset_ad_break import _update_asset_ad_break
from nomad_media_pip.common.asset.update_asset_language import _update_asset_language

from nomad_media_pip.common.content_metadata.add_custom_properties import _add_custom_properties
from nomad_media_pip.common.content_metadata.add_related_content import _add_related_content
from nomad_media_pip.common.content_metadata.add_tag_or_collection import _add_tag_or_collection
from nomad_media_pip.common.content_metadata.bulk_update_metadata import _bulk_update_metadata
from nomad_media_pip.common.content_metadata.create_tag_or_collection import _create_tag_or_collection
from nomad_media_pip.common.content_metadata.delete_related_content import _delete_related_content
from nomad_media_pip.common.content_metadata.delete_tag_or_collection import _delete_tag_or_collection
from nomad_media_pip.common.content_metadata.get_tag_or_collection import _get_tag_or_collection
from nomad_media_pip.common.content_metadata.remove_tag_or_collection import _remove_tag_or_collection

from nomad_media_pip.common.ping.ping import _ping
from nomad_media_pip.common.ping.ping_auth import _ping_auth

from nomad_media_pip.common.search.get_search import _get_search
from nomad_media_pip.common.search.post_search import _post_search

from nomad_media_pip.portal.account_updates.change_email import _change_email
from nomad_media_pip.portal.account_updates.change_password import _change_password
from nomad_media_pip.portal.account_updates.get_user import _get_user
from nomad_media_pip.portal.account_updates.update_user import _update_user

from nomad_media_pip.portal.content_groups.add_contents_to_content_group import _add_contents_to_content_group
from nomad_media_pip.portal.content_groups.create_content_group import _create_content_group
from nomad_media_pip.portal.content_groups.delete_content_group import _delete_content_group
from nomad_media_pip.portal.content_groups.get_content_group import _get_content_group
from nomad_media_pip.portal.content_groups.get_content_groups import _get_content_groups
from nomad_media_pip.portal.content_groups.get_portal_groups import _get_portal_groups
from nomad_media_pip.portal.content_groups.remove_contents_from_content_group import _remove_contents_from_content_group
from nomad_media_pip.portal.content_groups.rename_content_group import _rename_content_group
from nomad_media_pip.portal.content_groups.share_content_group_with_user import _share_content_group_with_user
from nomad_media_pip.portal.content_groups.stop_sharing_content_group_with_user import _stop_sharing_content_group_with_user

from nomad_media_pip.portal.guest_registration.guest_invite import _guest_invite
from nomad_media_pip.portal.guest_registration.register_guest import _register_guest
from nomad_media_pip.portal.guest_registration.remove_guest import _remove_guest

from nomad_media_pip.portal.media.clear_continue_watching import _clear_continue_watching
from nomad_media_pip.portal.media.clear_watchlist import _clear_watchlist
from nomad_media_pip.portal.media.create_form import _create_form
from nomad_media_pip.portal.media.get_content_cookies import _get_content_cookies
from nomad_media_pip.portal.media.get_default_site_config import _get_default_site_config
from nomad_media_pip.portal.media.get_dynamic_content import _get_dynamic_content
from nomad_media_pip.portal.media.get_dynamic_contents import _get_dynamic_contents
from nomad_media_pip.portal.media.get_media_group import _get_media_group
from nomad_media_pip.portal.media.get_media_item import _get_media_item
from nomad_media_pip.portal.media.get_my_content import _get_my_content
from nomad_media_pip.portal.media.get_my_group import _get_my_group
from nomad_media_pip.portal.media.get_site_config import _get_site_config
from nomad_media_pip.portal.media.media_search import _media_search

from nomad_media_pip.portal.media_builder.create_media_builder import _create_media_builder
from nomad_media_pip.portal.media_builder.create_media_builder_item import _create_media_builder_item
from nomad_media_pip.portal.media_builder.create_media_builder_items_add_annotations import _create_media_builder_items_add_annotations
from nomad_media_pip.portal.media_builder.create_media_builder_items_bulk import _create_media_builder_items_bulk
from nomad_media_pip.portal.media_builder.delete_media_builder import _delete_media_builder
from nomad_media_pip.portal.media_builder.delete_media_builder_item import _delete_media_builder_item
from nomad_media_pip.portal.media_builder.duplicate_media_builder import _duplicate_media_builder
from nomad_media_pip.portal.media_builder.get_media_builder import _get_media_builder
from nomad_media_pip.portal.media_builder.get_media_builder_ids_from_asset import _get_media_builder_ids_from_asset
from nomad_media_pip.portal.media_builder.get_media_builders import _get_media_builders
from nomad_media_pip.portal.media_builder.get_media_builder_items import _get_media_builder_items
from nomad_media_pip.portal.media_builder.move_media_builder_item import _move_media_builder_item
from nomad_media_pip.portal.media_builder.render_media_builder import _render_media_builder
from nomad_media_pip.portal.media_builder.update_media_builder import _update_media_builder

from nomad_media_pip.portal.saved_search.add_saved_search import _add_saved_search
from nomad_media_pip.portal.saved_search.delete_saved_search import _delete_saved_search
from nomad_media_pip.portal.saved_search.get_saved_search import _get_saved_search
from nomad_media_pip.portal.saved_search.get_saved_searches import _get_saved_searches
from nomad_media_pip.portal.saved_search.get_search_saved import _get_search_saved
from nomad_media_pip.portal.saved_search.get_search_saved_by_id import _get_search_saved_by_id
from nomad_media_pip.portal.saved_search.patch_saved_search import _patch_saved_search
from nomad_media_pip.portal.saved_search.update_saved_search import _update_saved_search

from nomad_media_pip.portal.video_tracking.get_video_tracking import _get_video_tracking


import time, threading, json, os, requests
from datetime import datetime
from typing import List
import tracemalloc
tracemalloc.start()

class Nomad_SDK:
	_instance = None
	_lock = threading.Lock()
	
	def __new__(cls, CONFIG):
		if cls._instance is None:
			with cls._lock:
				if cls._instance is None:
					cls._instance = super(Nomad_SDK, cls).__new__(cls)
					cls._instance.__init_singleton(CONFIG)
		return cls._instance
	
	def __init_singleton(self, CONFIG):
		self.config = CONFIG
		self.token = None
		self.refresh_token_val = None
		self.expiration_seconds = None
		self.user_session_id = None
		self.id = None
		self.debug_mode = self.config.get("debugMode", False)
		self.login()
		self.__start_refresh_token_thread()
	
	def __start_refresh_token_thread(self):
		REFRESH_TOKEN_THREAD = threading.Thread(target=self.__refresh_token_periodically, args=(self.expiration_seconds,))
		REFRESH_TOKEN_THREAD.daemon = True
		REFRESH_TOKEN_THREAD.start()
	
	def login(self):
		try:
			login_info = _login(self.config["serviceApiUrl"], self.config["username"], self.config["password"], self.debug_mode)
			if login_info == "Login info incorrect":
				raise Exception("Login info incorrect")
			self.token = login_info["token"]
			self.refresh_token_val = login_info["refreshToken"]
			self.expiration_seconds = login_info["expirationSeconds"]
			self.id = login_info["id"]
	
			return login_info["expirationSeconds"]
		except Exception as error:
			raise Exception(error.args[0])

	def refresh_token(self):
		try:
			token_info = _refresh_token(self.token, self.config["serviceApiUrl"], 
							   			self.refresh_token_val, self.debug_mode)
			self.token = token_info["token"]
	
			print(datetime.now().strftime('%H:%M:%S'), "Token refreshed:", self.token, sep=" ")
		except Exception as error:
			raise Exception(error.args[0])
	
	
	def __refresh_token_periodically(self, SECONDS):
		while True:
			try:
				time.sleep(SECONDS - 100)

				self.refresh_token()
			except Exception as error:
				print(datetime.now().strftime('%H:%M:%S'), "Refresh token failed", sep=" ")
				raise Exception(error.args[0])
			
	
	# admin
	# asset upload
	"""
	Description:
	Uploads a file to the system.
	Parameters:
	NAME (str | None): The name of the file being uploaded.
	EXISTING_ASSET_ID (str | None): The Existing AssetId (file) that should be 
	overwritten with this upload. Note that by specifying this attribute then the parentId, 
	relativePath and displayName are all ignored.
	RELATED_CONTENT_ID (str | None): The Content ID of the related content record 
	to associate this asset to. Note that by specifying this attribute then the parentId and 
	relativePath attributes are both ignored.
	UPLOAD_OVERWRITE_OPTION (str): The overwrite option for the upload. 
	The option you want to use when uploading the asset. The options are continue, replace,
	and cancel. Continue continues the upload from where it left off. Replace replaces an 
	existing asset. Replace is the one you want to use if you are starting a new upload. 
	Cancel cancels an uploading asset.
	FILE (str): The filename to upload - or the full or relative path of the file.
	This is ignored if the ExistingAssetId or if the RelatedContentId has a value.
	PARENT_ID (str | None): The Parent AssetId (folder) to add the upload to. 
	Note that if there is a full relativePath, then it is appended to this parent path. 
	If this value is omitted then the file will be added to the predefined incoming folder.
	This is ignored if the ExistingAssetId or if the RelatedContentId has a value.
	LANGUAGE_ID (str | None): The language of the asset to upload. 
	If this is left blank then the default system language is used.
	Returns:
	dict: The asset information
	Exception: If the upload fails.
	"""
	def upload_asset(self, NAME: str | None, EXISTING_ASSET_ID: str | None, 
					RELATED_CONTENT_ID: str | None, UPLOAD_OVERWRITE_OPTION: str, FILE: str, 
					PARENT_ID: str | None, LANGUAGE_ID) -> dict:
		START_UPLOAD_INFO = None
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), f"Uploading asset {NAME}", sep=" ")
	
			print("Start upload")
			START_UPLOAD_INFO = _start_upload(self.token, self.config["serviceApiUrl"], 
				NAME, EXISTING_ASSET_ID, RELATED_CONTENT_ID, UPLOAD_OVERWRITE_OPTION, FILE, 
				PARENT_ID, LANGUAGE_ID, self.config["debugMode"])
	
			_multi_thread_upload(self.token, self.config["serviceApiUrl"], FILE, 
				START_UPLOAD_INFO, self.config["debugMode"])
	
			_upload_complete_asset(self.token, self.config["serviceApiUrl"], 
				START_UPLOAD_INFO["id"], self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Upload complete", sep=" ")
	
			return START_UPLOAD_INFO["assetId"]
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Upload failed", sep=" ")

			if START_UPLOAD_INFO:
				_cancel_upload(self.token, self.config["serviceApiUrl"], 
					START_UPLOAD_INFO["id"], self.debug_mode)
			raise Exception(error.args[0])

	"""
	Description:
	Uploads a related asset to the specified existing asset ID.
	Parameters:
	EXISTING_ASSET_ID (str): Gets or sets the Existing AssetId (file) that should be 
	overwritten with this upload. Note that by specifying this attribute then the parentId, 
	relativePath and displayName are all ignored.
	RELATED_ASSET_ID (str | None): Gets or sets the related asset ID of the existingAsset that
	we're replacing. If this is used, most of the other properties are not needed.
	NEW_RELATED_ASSET_METATYPE (str | None): Gets or sets the type of the related asset metadata to 
	be created for a given ExistingAssetId. If specified, ExistingAssetId has to have a value defined.
	UPLOAD_OVERWRITE_OPTION (str): The overwrite option for the upload.
	The option you want to use when uploading the asset. The options are continue, replace, and cancel.
	Continue continues the upload from where it left off. Replace replaces an existing asset.
	Replace is the one you want to use if you are starting a new upload. Cancel cancels an uploading asset.
	FILE (str): The filename to upload - or the full or relative path of the file.
	This is ignored if the ExistingAssetId or if the RelatedContentId has a value.
	LANGUAGE_ID (str | None): The language of the asset to upload.
	If this is left blank then the default system language is used.
	Returns:
	dict: The asset information
	Exception: If the upload fails.
	"""
	def upload_related_asset(self, EXISTING_ASSET_ID: str, RELATED_ASSET_ID: str | None,
						  	 NEW_RELATED_ASSET_METATYPE: str | None,
							 UPLOAD_OVERWRITE_OPTION: str, FILE: str, LANGUAGE_ID: str | None) -> dict:
		START_UPLOAD_INFO = None
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Uploading related asset", sep=" ")
	
			print("Start upload")
			START_UPLOAD_INFO = _start_related_asset_upload(self.token, self.config["serviceApiUrl"],
				EXISTING_ASSET_ID, RELATED_ASSET_ID, NEW_RELATED_ASSET_METATYPE, 
				UPLOAD_OVERWRITE_OPTION, FILE, LANGUAGE_ID, 
				self.config["debugMode"])
	
			_multi_thread_upload(self.token, self.config["serviceApiUrl"], FILE, 
				START_UPLOAD_INFO, self.config["debugMode"])
	
			_upload_complete_asset(self.token, self.config["serviceApiUrl"], 
				START_UPLOAD_INFO["id"], self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Upload complete", sep=" ")

			DETAILS = _get_asset_details(self.token, self.config["serviceApiUrl"], EXISTING_ASSET_ID,
								self.config["apiType"], self.debug_mode)
			
			RELATED_ASSET = next((asset for asset in DETAILS['relatedAssets'] if os.path.basename(FILE) in asset['url']), None)

			return RELATED_ASSET["id"]
	
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Upload failed", sep=" ")

			if START_UPLOAD_INFO:
				_cancel_upload(self.token, self.config["serviceApiUrl"], 
					START_UPLOAD_INFO["id"], self.debug_mode)
			raise Exception(error.args[0])


	# audit
	"""
	Description:
	Gets the audit information for the specified content ID.
	Parameters:
	CONTENT_ID (str): The ID of the content to get the audit information for.
	Returns:
	dict: Returns the audit information.
	Exception: An error is thrown if the audit information fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_audit(self, CONTENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting audit", sep=" ")

			AUDIT = _get_audit(self.token, self.config["serviceApiUrl"], CONTENT_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get audit complete", sep=" ")

			return AUDIT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get audit failed", sep=" ")
			raise Exception(error.args[0])
	
	# config
	"""
	Description:
	Clears the server cache.
	Returns:
	None: Clears the server cache.
	Exception: An error is thrown if the server cache fails to clear.
	Exception: An error is thrown if the API type is not admin.
	"""
	def clear_server_cache(self) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Clearing server cache", sep=" ")

			_clear_server_cache(self.token, self.config["serviceApiUrl"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Clear server cache complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Clear server cache failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the specified config.
	Parameters:
	CONFIG_TYPE (int): The type of config to get. 1 - Admin, 2 - Lambda, 3 - Groundtruth
	Returns:
	dict: Returns the config information.
	Exception: An error is thrown if the config fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_config(self, CONFIG_TYPE: int) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting config", sep=" ")

			CONFIG = _get_config(self.token, self.config["serviceApiUrl"], CONFIG_TYPE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get config complete", sep=" ")

			return CONFIG
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get config failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the server time.
	Returns:
	dict: Returns the server time information.
	Exception: An error is thrown if the server time fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_server_time(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting server time", sep=" ")

			SERVER_TIME = _get_server_time(self.token, self.config["serviceApiUrl"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get server time complete", sep=" ")

			return SERVER_TIME
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get server time failed", sep=" ")
			raise Exception(error.args[0])

	# content
	"""
	Description:
	Creates a new content.
	Parameters:
	CONTENT_DEFINITION_ID (str): The ID of the content definition
	LANGUAGE_ID (str, None): The language id of the asset to upload.
	If this is left blank then the default system language is used.
	Returns:
	dict: The content information of the newly created content.
	Exception: If the API type is not admin.
	Exception: If the creation fails.
	"""
	def create_content(self, CONTENT_DEFINITION_ID: str, LANGUAGE_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Creating content", sep=" ")
	
			CONTENT_ID = _create_content(self.token, self.config["serviceApiUrl"], 
				CONTENT_DEFINITION_ID, LANGUAGE_ID, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Create content complete", sep=" ")
	
			return CONTENT_ID
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create content failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deactivates the specified user track.
	Parameters:
	SESSION_ID (str): The session ID of the user track to deactivate.
	CONTENT_ID (str): The content ID of the user track to deactivate.
	CONTENT_DEFINITION_ID (str): The content definition ID of the user track to deactivate.
	DEACTIVATE (bool): Whether to deactivate the user track.
	Returns:
	None: Deactivates the specified user track.
	Exception: An error is thrown if the user track fails to deactivate.
	Exception: An error is thrown if the API type is not admin.
	"""
	def deactivate_content_user_track(self, SESSION_ID: str, CONTENT_ID: str,
								      CONTENT_DEFINITION_ID: str, 
									  DEACTIVATE: bool) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deactivating content user track", sep=" ")

			_deactivate_content_user_track(self.token, self.config["serviceApiUrl"], SESSION_ID, 
				CONTENT_ID, CONTENT_DEFINITION_ID, DEACTIVATE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Deactivate content user track complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Deactivate content user track failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a content.
	Parameters:
	CONTENT_ID (str): The ID of the content to delete.
	CONTENT_DEFINITION_ID (str): The ID of the content definition the content belongs to.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the deletion fails.
	"""
	def delete_content(self, CONTENT_ID: str, CONTENT_DEFINITION_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Deleting content", sep=" ")
	
			_delete_content(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Delete content complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete content failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a content.
	Parameters:
	CONTENT_ID (str): The ID of the content to get.
	CONTENT_DEFINITION_ID: The ID of the content definition the content belongs to.
	IS_REVISION (bool | None): Indicates if the content is a revision.
	Defaults to false.
	Returns:
	dict: The content information.
	Exception: If the API type is not admin.
	Exception: If the get fails.
	"""
	def get_content(self, CONTENT_ID, CONTENT_DEFINITION_ID, IS_REVISION) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Geting content", sep=" ")
	
			CONTENT = _get_content(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, IS_REVISION, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Get content complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content failed", sep=" ")
			raise Exception(error.args[0])
	
	"""
	Description:
	Gets the specified content user track.
	Parameters:
	CONTENT_ID (str): The ID of the content to get the user track for.
	CONTENT_DEFINITION_ID (str): The ID of the content definition to use.
	SORT_COLUMN (str | None): The column to sort by.
	IS_DESC (bool | None): Whether to sort descending.
	PAGE_INDEX (int | None): The page index to get.
	PAGE_SIZE (int | None): The page size to get.
	Returns:
	dict: Returns the content user track information.
	Exception: An error is thrown if the content user track fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_content_user_track(self, CONTENT_ID: str, CONTENT_DEFINITION_ID: str, 
							   SORT_COLUMN: str, IS_DESC: bool, PAGE_INDEX: int | None, 
							   PAGE_SIZE: int | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting content user track", sep=" ")

			CONTENT = _get_content_user_track(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, SORT_COLUMN, IS_DESC, PAGE_INDEX, PAGE_SIZE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get content user track complete", sep=" ")

			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content user track failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets the specified content user track touch.
	Parameters:
	CONTENT_ID (str): The ID of the content to get the user track touch for.
	CONTENT_DEFINITION_ID (str): The ID of the content definition to use.
	Returns:
	dict: Returns the content user track touch information.
	Exception: An error is thrown if the content user track touch fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_content_user_track_touch(self, CONTENT_ID: str, CONTENT_DEFINITION_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting content user track touch", sep=" ")

			CONTENT = _get_content_user_track_touch(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, CONTENT_DEFINITION_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get content user track touch complete", sep=" ")

			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content user track touch failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates a content.
	Parameters:
	CONTENT_ID (str): The ID of the content to update.
	CONTENT_DEFINITION_ID: The ID of the content definition the content belongs to.
	PROPERTIES (dict): The properties to update.
	LANGUAGE_ID (str | None): The language id of the asset to upload.
	If this is left blank then the default system language is used.
	Returns:
	dict: The content information of the updated content.
	Exception: If the API type is not admin.
	Exception: If the update fails.
	"""
	def update_content(self, CONTENT_ID: str, CONTENT_DEFINITION_ID: str, PROPERTIES: dict, 
					   LANGUAGE_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Updating content", sep=" ")
	
			_update_content(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, PROPERTIES, LANGUAGE_ID, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Update content complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update content failed", sep=" ")
			raise Exception(error.args[0])
	
	# content admin
	"""
	Description:
	Adds a custom property to the specified content.
	Parameters:
	CONTENT_ID (str): The ID of the content to add the custom property to.
	NAME (str | None): The name of the custom property.
	DATE (str | None): The date of the custom property.
	CUSTOM_PROPERTIES (dict):  A list of custom properties that should be saved for the 
	asset. To remove a property value, set the value to None
	Returns:
	dict: The information of the added custom properties.
	Exception: If the API type is not admin.
	Exception: If the add custom properties fails.
	"""
	def add_custom_property(self, CONTENT_ID: str, NAME: str | None, DATE: str | None,
						 	CUSTOM_PROPERTIES: dict) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), "Adding custom properties", sep=" ")
	
			CONTENT = _add_custom_properties(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, NAME, DATE, CUSTOM_PROPERTIES, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Add custom properties complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add custom properties failed", sep=" ")
			raise Exception(error.args[0])
		
	
	"""
	Description:
	Adds a related content to the specified content.
	Parameters:
	CONTENT_ID (str): The ID of the content to add the related content to.
	RELATED_CONTENT_ID (str): The ID of the related content.
	CONTENT_DEFINITION (str): The content definition of the related content.
	Returns:
	dict: The information of the added related content.
	Exception: If the add related content fails.
	"""
	def add_related_content(self, CONTENT_ID: str, RELATED_CONTENT_ID: str, 
						 	CONTENT_DEFINITION: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Adding related content", sep=" ")
	
			CONTENT = _add_related_content(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, RELATED_CONTENT_ID, CONTENT_DEFINITION, self.config["apiType"],
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Add related content complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add related content failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Adds a tag or collection to the specified content.
	Parameters:
	TYPE (str): The type of the tag or collection. The options are tag and collection.
	CONTENT_ID (str): The ID of the content to add the tag or collection to.
	CONTENT_DEFINITION (str): The content definition of the tag or collection.
	TAG_NAME (str): The name of the tag or collection.
	TAG_ID (str | None): The ID of the tag or collection.
	CREATE_NEW (bool | None): Indicates if a new tag or collection should be created.
	Returns:
	dict: The information of the added tag or collection.
	Exception: If the add tag or collection fails.
	"""
	def add_tag_or_collection(self, TYPE: str, CONTENT_ID: str, CONTENT_DEFINITION: str, 
						   	  TAG_NAME: str, TAG_ID: str | None, CREATE_NEW: bool | None) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), f"Adding {TYPE} to content {CONTENT_ID}", sep=" ")
	
			CONTENT = _add_tag_or_collection(self.token, self.config["serviceApiUrl"], TYPE, 
				CONTENT_ID, CONTENT_DEFINITION, TAG_NAME, TAG_ID, CREATE_NEW, self.config["apiType"],
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), f"Added {TYPE} to content {CONTENT_ID}", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), f"Adding {TYPE} to content {CONTENT_ID} failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates the metadata for the specified content.
	Parameters:
	CONTENT_IDS (list of str): The IDs of the content to update the metadata for.
	COLLECTION_IDS (list of str | None): The IDs of the collections to update the metadata for.
	RELATED_CONTENT_IDS (list of str | None): The IDs of the related content to update.
	TAG_IDS (list of str | None): The IDs of the tags to update the metadata for.
	SCHEMA_NAME (str | None): The name of the schema to use.
	Returns:
	None: A promise that resolves when the metadata is updated.
	Exception: An error is thrown if the metadata fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def bulk_update_metadata(self, CONTENT_IDS: List[str], COLLECTION_IDS: List[str], 
						     RELATED_CONTENT_IDS: List[str], TAG_IDS: List[str], 
							 SCHEMA_NAME: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Performing Bulk Update", sep=" ")

			_bulk_update_metadata(self.token, self.config["serviceApiUrl"], CONTENT_IDS, 
				COLLECTION_IDS, RELATED_CONTENT_IDS, TAG_IDS, SCHEMA_NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Bulk Update complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Bulk Update failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Creates a tag or collection.
	Parameters:
	TYPE (str): Specify if the content being managed is a tag or a collection.
	TAG_NAME (str): The name of the tag or collection to create.
	Returns:
	dict: Returns the id of the created tag or collection.
	Exception: An error is thrown if the tag or collection fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_tag_or_collection(self, TYPE: str, TAG_NAME: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), f"Creating {TYPE}", sep=" ")

			CONTENT = _create_tag_or_collection(self.token, self.config["serviceApiUrl"], 
				TYPE, TAG_NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), f"Create {TYPE} complete", sep=" ")

			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), f"Create {TYPE} failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a related content from the specified content.
	Parameters:
	CONTENT_ID (str): The ID of the content to delete the related content from.
	RELATED_CONTENT_ID (str): The ID of the related content.
	CONTENT_DEFINITION (str): The content definition of the related content.
	Returns:
	dict: The information of the deleted related content.
	Exception: If the delete related content fails.
	"""
	def delete_related_content(self, CONTENT_ID: str, RELATED_CONTENT_ID: str, 
							   CONTENT_DEFINITION: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Deleting related content", sep=" ")
	
			CONTENT = _delete_related_content(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, RELATED_CONTENT_ID, CONTENT_DEFINITION, self.config["apiType"],
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Delete related content complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete related content failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a tag or collection from the specified content.
	Parameters:
	TYPE (str): The type of the tag or collection. The options are tag and collection.
	TAG_ID (str): The ID of the tag or collection.
	Returns:
	dict: The id of the tag.
	Exception: If the API type is not admin.
	Exception: If the delete tag or collection fails.
	"""
	def delete_tag_or_collection(self, TYPE: str, TAG_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
	
			print(datetime.now().strftime('%H:%M:%S'), f"Deleting {TYPE}", sep=" ")
	
			CONTENT = _delete_tag_or_collection(self.token, self.config["serviceApiUrl"], 
				TYPE, TAG_ID, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), f"Delete {TYPE} complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), f"Delete {TYPE} failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a tag or collection from the specified content.
	Parameters:
	TYPE (str): The type of the tag or collection. The options are tag and collection.
	TAG_ID (str): The ID of the tag or collection.
	Returns:
	dict: The id of the tag.
	Exception: If the API type is not admin.
	Exception: If the delete tag or collection fails.
	"""
	def get_tag_or_collection(self, TYPE: str, TAG_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), f"Getting {TYPE}", sep=" ")

			CONTENT = _get_tag_or_collection(self.token, self.config["serviceApiUrl"], 
				TYPE, TAG_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), f"Get {TYPE} complete", sep=" ")

			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), f"Get {TYPE} failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Removes a tag or collection from the specified content.
	Parameters:
	TYPE (str): The type of the tag or collection. The options are tag and collection.
	CONTENT_ID (str): The ID of the content to remove the tag or collection from.
	CONTENT_DEFINITION_ID (str): The content definition of the tag or collection.
	TAG_ID (str): The ID of the tag or collection.
	Returns:
	dict: The information of the removed tag or collection.
	Exception: If the remove tag or collection fails.
	"""
	def remove_tag_or_collection(self, TYPE: str, CONTENT_ID: str, 
							  	 CONTENT_DEFINITION_ID: str, TAG_ID: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start remove tag or collection", sep=" ")
	
			CONTENT = _remove_tag_or_collection(self.token, self.config["serviceApiUrl"], 
				TYPE, CONTENT_ID, CONTENT_DEFINITION_ID, TAG_ID, self.config["apiType"],
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Remove tag or collection complete", sep=" ")
	
			return CONTENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Remove tag or collection failed", sep=" ")
			raise Exception(error.args[0])

	# Event
	"""
	Description:
	Adds a live schedule to an event and updated live schedule attached to event.
	Parameters:
	EVENT_ID (str): The ID of the event to add the live schedule to.
	SLATE_VIDEO (dict, None): The slate video ID of the event. Format: {"id": string, "description": string }
	PREROLL_VIDEO (dict, None): The preroll video of the event. Format: {"id": string, "description": string }
	POSTROLL_VIDEO (dict, None): The postroll video of the event. Format: {"id": string, "description": string }
	IS_SECURE_OUTPUT (bool, None): Whether the event is secure output.
	ARCHIVE_FOLDER (dict, None): The archive folder of the event. Format: { id: string, description: string }
	PRIMARY_LIVE_INPUT (dict, None): The live input A ID of the event. Format: { id: string, description: string }
	BACKUP_LIVE_INPUT (dict, None): The live input B ID of the event. Format: { id: string, description: string }
	PRIMARY_LIVESTREAM_INPUT_URL (str, None): The primary live stream URL of the event.
	BACKUP_LIVESTREAM_INPUT_URL (str, None): The backup live stream URL of the event.
	EXTERNAL_OUTPUT_PROFILES (list of dict, None): The external output profiles of the event.
	Returns:
	None: A promise that resolves when the live event schedule is created.
	Exception: An error is thrown if the live event schedule fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def add_live_schedule_to_event(self, EVENT_ID: str, SLATE_VIDEO: dict | None, 
		PREROLL_VIDEO: dict | None, POSTROLL_VIDEO: dict | None, IS_SECURE_OUTPUT: bool | None, 
		ARCHIVE_FOLDER: dict | None, PRIMARY_LIVE_INPUT: dict | None, 
		BACKUP_LIVE_INPUT: dict | None, PRIMARY_LIVESTREAM_INPUT_URL: dict | None,
		BACKUP_LIVESTREAM_INPUT_URL: dict | None, EXTERNAL_OUTPUT_PROFILES: List[dict] | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Adding live schedule to event", sep=" ")

			_add_live_schedule_to_event(self.token, self.config["serviceApiUrl"], EVENT_ID, SLATE_VIDEO, 
				PREROLL_VIDEO, POSTROLL_VIDEO, IS_SECURE_OUTPUT, ARCHIVE_FOLDER, PRIMARY_LIVE_INPUT, 
				BACKUP_LIVE_INPUT, PRIMARY_LIVESTREAM_INPUT_URL, BACKUP_LIVESTREAM_INPUT_URL, 
				EXTERNAL_OUTPUT_PROFILES, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Add live schedule to event complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add live schedule to event failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Creates and updates an event.
	Parameters:
	CONTENT_ID (str, None): The content id of the event to update. None for create.
	CONTENT_DEFINITION_ID (str): The content definition id of the event.
	NAME (str | None): The name of the event.
	START_DATETIME (str): The start date time of the event.
	END_DATETIME (str): The end date time of the event.
	EVENT_TYPE (dict): The event type of the event. Format: { id: string, description: string }
	SERIES (dict | None): The series of the event. Format: { id: string, description: string }
	IS_DISALED (bool, None): Whether the event is disabled.
	OVERRIDE_SERIES_PROPERTIES (bool): Whether to override the series properties.
	SERIES_PROPERTIES (dict | None): The properties of the event.
	
	Returns:
	dict: Returns the information of the created and updated event.
	Exception: An error is thrown if the event fails to create and update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_and_update_event(self, CONTENT_ID: str | None, CONTENT_DEFINITION_ID: str, 
								NAME: str | None, START_DATETIME: str, END_DATETIME: str,
								EVENT_TYPE: dict, SERIES: dict | None,
								IS_DISABLED: bool | None, OVERRIDE_SERIES_PROPERTIES,
								SERIES_PROPERTIES: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating and updating event", sep=" ")

			EVENT = _create_and_update_event(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, CONTENT_DEFINITION_ID, NAME, START_DATETIME, END_DATETIME,
				EVENT_TYPE, SERIES, IS_DISABLED, OVERRIDE_SERIES_PROPERTIES, 
				SERIES_PROPERTIES, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Create and update event complete", sep=" ")

			return EVENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create and update event failed", sep=" ")
			raise Exception(error.args[0])	
		
	"""
	Description:
	Deletes an event.
	Parameters:
	CONTENT_ID (str): The ID of the event to delete.
	CONTENT_DEFINITION_ID (str): The content definition ID of the event to delete.
	Returns:
	None: A promise that resolves when the event is deleted.
	Exception: An error is thrown if the event fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_event(self, CONTENT_ID: str, CONTENT_DEFINITION_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting event", sep=" ")

			_delete_event(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete event complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Extends the live schedule of an event.
	Parameters:
	EVENT_ID (str): The ID of the event to extend the live schedule of.
	RECURRING_DAYS (list of dict): The days of the week to extend the live schedule of. Format: [{ id: string, description: string },]
	RECURRING_WEEKS (int): The number of weeks to extend the live schedule of.
	END_DATE (str, None): The end date to extend the live schedule of.
	Returns:
	None: A promise that resolves when the live schedule is extended.
	Exception: An error is thrown if the live schedule fails to extend.
	Exception: An error is thrown if the API type is not admin.
	"""
	def extend_live_schedule(self, EVENT_ID: str, RECURRING_DAYS: List[dict],
							 RECURRING_WEEKS: int, END_DATE: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Extending live schedule", sep=" ")

			_extend_live_schedule(self.token, self.config["serviceApiUrl"], EVENT_ID, 
				RECURRING_DAYS, RECURRING_WEEKS, END_DATE, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Extend live schedule complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Extend live schedule failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets the live schedule of an event.
	Parameters:
	EVENT_ID (str): The ID of the event to get the live schedule of.
	Returns:
	dict: Returns the information of the live schedule.
	Exception: An error is thrown if the live schedule fails to retrieve.
	Exception: An error is thrown if the API type is not admin.
	"""	
	def get_live_schedule(self, EVENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting live schedule", sep=" ")

			EVENT = _get_live_schedule(self.token, self.config["serviceApiUrl"], EVENT_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live schedule complete", sep=" ")

			return EVENT
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Starts the live schedule of an event.
	Parameters:
	EVENT_ID (str): The ID of the event to start the live schedule of.
	Returns:
	None: A promise that resolves when the live schedule is started.
	Exception: An error is thrown if the live schedule fails to start.
	Exception: An error is thrown if the API type is not admin.
	"""
	def start_live_schedule(self, EVENT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Starting live schedule", sep=" ")

			_start_live_schedule(self.token, self.config["serviceApiUrl"], EVENT_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Start live schedule complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Start live schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Stops the live schedule of an event.
	Parameters:
	EVENT_ID (str): The ID of the event to stop the live schedule of.
	Returns:
	None: A promise that resolves when the live schedule is stopped.
	Exception: An error is thrown if the live schedule fails to stop.
	Exception: An error is thrown if the API type is not admin.
	"""
	def stop_live_schedule(self, EVENT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Stopping live schedule", sep=" ")

			_stop_live_schedule(self.token, self.config["serviceApiUrl"], EVENT_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Stop live schedule complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Stop live schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	# Live Channel
	"""
	Description:
	Clips a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel to clip.
	START_TIME_CODE (str, None): The start time code of the live channel to clip.
	END_TIME_CODE (str, None): The end time code of the live channel to clip.
	TITLE (str, None): The title of the live channel to clip.
	OUTPUT_FOLDER_ID (str): The output folder ID of the live channel to clip.
	TAGS (list of dict, None): The tags of the live channel to clip. Format: [{ id: string, description: string },]
	COLLECTIONS (list of dict, None): The collections of the live channel to clip. Format: [{ id: string, description: string },]
	RELATED_CONTENTS (list of dict, None): The related contents of the live channel to clip. Format: [{ id: string, description: string },]
	VIDEO_BITRATE (int, None): The video bitrate of the live channel to clip.
	AUDIO_TRACKS (list of dict, None): The audio tracks of the live channel to clip.
	Returns:
	dict: Returns the information of the clipped live channel.
	Exception: An error is thrown if the live channel fails to clip.
	Exception: An error is thrown if the API type is not admin.
	"""
	def clip_live_channel(self, LIVE_CHANNEL_ID: str, START_TIME_CODE: str | None, 
						  END_TIME_CODE: str | None, TITLE: str | None, 
						  OUTPUT_FOLDER_ID: str, TAGS: List[dict] | None, 
						  COLLECTIONS: List[dict] | None, RELATED_CONTENTS: List[dict] | None, 
						  VIDEO_BITRATE: int | None, AUDIO_TRACKS: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Clipping live channel", sep=" ")

			LIVE_CHANNEL = _clip_live_channel(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, START_TIME_CODE, END_TIME_CODE, TITLE, OUTPUT_FOLDER_ID, TAGS, 
				COLLECTIONS, RELATED_CONTENTS, VIDEO_BITRATE, AUDIO_TRACKS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Clip live channel complete", sep=" ")

			return LIVE_CHANNEL
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Clip live channel failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Creates a live channel.
	Parameters:
	NAME (str | None): The name of the live channel.
	THUMBNAIL_IMAGE_ID (str | None): The thumbnail image ID of the live channel.
	ARCHIVE_FOLDER_ASSET_ID (str | None): The archive folder asset ID of the live channel.
	ENABLE_HIGH_AVAILABILITY (bool | None): Indicates if the live channel is enabled for 
	high availability.
	ENABLE_LIVE_CLIPPING (bool | None): Indicates if the live channel is enabled for live 
	clipping.
	IS_SECURE_OUTPUT (bool): Indicates if the live channel is secure output.
	IS_OUTPUT_SCREENSHOT (bool): Indicates if the live channel is output screenshot.
	TYPE (str): The type of the live channel. The types are External, IVS, Normal,
	and Realtime.
	EXTERNAL_SERVICE_API_URL (str | None): The external service API URL of the live channel.
	Only required if the type is External.
	SECURITY_GROUPS (string | None): The security groups of the live channel.
	The security groups are: Content Manager, Everyone, and Guest.
	Returns:
	dict: The information of the live channel.
	Exception: If the API type is not admin.
	Exception: If the create live channel fails.
	"""
	def create_live_channel(self, NAME: str | None, THUMBNAIL_IMAGE_ID: str | None, 
						 	ARCHIVE_FOLDER_ASSET_ID: str | None, 
							ENABLE_HIGH_AVAILABILITY: bool | None, 
							ENABLE_LIVE_CLIPPING: bool | None, IS_SECURE_OUTPUT: bool,
							IS_OUTPUT_SCREENSHOT: bool, TYPE: str | None, 
							EXTERNAL_SERVICE_API_URL: str | None, SECURITY_GROUPS: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start create live channel", sep=" ")
	
			LIVE_CHANNEL_INFO = _create_live_channel(self.token, self.config["serviceApiUrl"], 
				NAME, THUMBNAIL_IMAGE_ID, ARCHIVE_FOLDER_ASSET_ID, ENABLE_HIGH_AVAILABILITY, 
				ENABLE_LIVE_CLIPPING, IS_SECURE_OUTPUT, IS_OUTPUT_SCREENSHOT, TYPE, 
				EXTERNAL_SERVICE_API_URL, SECURITY_GROUPS, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Create live channel complete", sep=" ")
	
			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create live channel failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	DELETE_INPUTS (bool | None): Indicates if the live channel inputs should be deleted.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the delete live channel fails.
	"""
	def delete_live_channel(self, LIVE_CHANNEL_ID: str, DELETE_INPUTS: bool) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start delete live channel", sep=" ")
	
			_delete_live_channel(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				DELETE_INPUTS, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Delete live channel complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete live channel failed", sep=" ")
			raise Exception(error.args[0]) 
		
	"""
	Description:
	Gets the live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	Returns:
	dict: The information of the live channel.
	Exception: If the API type is not admin.
	Exception: If the get live channel fails.
	"""
	def get_live_channel(self, LIVE_CHANNEL_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get live channel", sep=" ")
	
			LIVE_CHANNEL_INFO = _get_live_channel(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Get live channel complete", sep=" ")
	
			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live channel failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets all the live channels.
	Returns:
	dict: The information of the live channels.
	Exception: If the API type is not admin.
	Exception: If the get live channels fails.
	"""
	def get_live_channels(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get live channels", sep=" ")
	
			LIVE_CHANNEL_INFO = _get_live_channels(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Get live channels complete", sep=" ")
	
			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live channels failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Refreshes Live Channels
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the refresh live channels fails.
	"""
	def live_channel_refresh(self) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start live channel refresh", sep=" ")

			_live_channel_refresh(self.token, self.config["serviceApiUrl"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Live channel refresh complete", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the next live channel event
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	Returns:
	dict: The information of the next live channel event.
	Exception: If the API type is not admin.
	Exception: If the get next live channel event fails.
	"""
	def next_event(self, LIVE_CHANNEL_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get next live channel event", sep=" ")

			LIVE_CHANNEL_INFO = _next_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get next live channel event complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get next live channel event failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Starts a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the start live channel fails.
	"""
	def start_live_channel(self, LIVE_CHANNEL_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start start live channel", sep=" ")
	
			_start_live_channel(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Start live channel complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Start live channel failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Starts output tracking for a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the start output tracking fails.
	"""
	def start_output_tracking(self, LIVE_CHANNEL_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start start output tracking", sep=" ")

			_start_output_tracking(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Start output tracking complete", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Stops a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the stop live channel fails.
	"""
	def stop_live_channel(self, LIVE_CHANNEL_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start stop live channel", sep=" ")
	
			_stop_live_channel(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Stop live channel complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Stop live channel failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	NAME (str | None): The name of the live channel.
	THUMBNAIL_IMAGE_ID (str | None): The thumbnail image ID of the live channel.
	ARCHIVE_FOLDER_ASSET_ID (str | None): The archive folder asset ID of the live channel.
	ENABLE_HIGH_AVAILABILITY (bool | None): Indicates if the live channel is enabled for
	high availability.
	ENABLE_LIVE_CLIPPING (bool | None): Indicates if the live channel is enabled for live
	clipping.
	IS_SECURE_OUTPUT (bool | None): Indicates if the live channel is secure output.
	IS_OUTPUT_SCREENSHOT (bool | None): Indicates if the live channel is output screenshot.
	TYPE (str | None): The type of the live channel. The types are External, IVS, Normal,
	and Realtime.
	EXTERNAL_SERVICE_API_URL (str | None): The external service API URL of the live channel.
	Only required if the type is External.
	SECURITY_GROUPS (str | None): The security groups of the live channel.
	The security groups are: Content Manager, Everyone, and Guest.
	Returns:
	dict: The information of the live channel.
	Exception: If the API type is not admin.
	Exception: If the update live channel fails.
	"""
	def update_live_channel(self, LIVE_CHANNEL_ID: str, NAME: str | None, 
						 	THUMBNAIL_IMAGE_ID: str | None, ARCHIVE_FOLDER_ASSET_ID: str | None,
							ENABLE_HIGH_AVAILABILITY: bool | None, 
							ENABLE_LIVE_CLIPPING: bool | None, IS_SECURE_OUTPUT: bool,
							IS_OUTPUT_SCREENSHOT: bool, TYPE: str | None, 
							EXTERNAL_SERVICE_API_URL: str | None, SECURITY_GROUPS: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start update live channel", sep=" ")
	
			LIVE_CHANNLEL_INFO = _update_live_channel(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, NAME, THUMBNAIL_IMAGE_ID, ARCHIVE_FOLDER_ASSET_ID,
				ENABLE_HIGH_AVAILABILITY, ENABLE_LIVE_CLIPPING, IS_SECURE_OUTPUT, 
				IS_OUTPUT_SCREENSHOT, TYPE, EXTERNAL_SERVICE_API_URL, SECURITY_GROUPS, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Update live channel complete", sep=" ")
	
			return LIVE_CHANNLEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update live channel failed", sep=" ")
			raise Exception(error.args[0])

	# Live Input	
	"""
	Description:
	Creates a live input.
	Parameters:
	NAME (str | None): The name of the live input.
	SOURCE (str | None): The souce of the live input.
	TYPE (str | None): The type of the live input. The types are RTMP_PULL, RTMP_PUSH,
	RTP_PUSH, UDP_PUSH and URL_PULL
	IS_STANDARD (bool | None): Indicates if the live input is standard.
	VIDEO_ASSET_ID (str | None): The video asset ID of the live input.
	DESTINATIONS (list[dict] | None): The destinations of the live input. Sources must be URLs and are
	only valid for input types: RTMP_PUSH, URL_PULL, and MP4_FILE.
	dict format: {"ip": "string | None", "port": "string | None", "url": "string | None"}
	SOURCES (list[dict] | None): The sources of the live input. Sources must be URLs and are
	only valid for input types: RTMP_PULL.
	dict format: {"ip": "string | None", "port": "string | None", "url": "string | None"}
	Returns:
	dict: The information of the live input.
	Exception: If the API type is not admin.
	Exception: If the create live input fails.
	"""
	def create_live_input(self, NAME: str | None, SOURCE: str | None, TYPE: str | None, 
					   	  IS_STANDARD: bool | None, VIDEO_ASSET_ID: str | None, 
						  DESTINATIONS: List[dict], SOURCES: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start create live input", sep=" ")

			LIVE_CHANNEL_INFO = _create_live_input(self.token, self.config["serviceApiUrl"], 
				NAME, SOURCE, TYPE, IS_STANDARD, VIDEO_ASSET_ID, DESTINATIONS, SOURCES, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create live input complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create live input failed", sep=" ")
			raise Exception(error.args[0])
        
	"""
	Description:
	Deletes a live input.
	Parameters:
	LIVE_INPUT_ID (str): The ID of the live input.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the delete live input fails.
	"""
	def delete_live_input(self, LIVE_INPUT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start delete live input", sep=" ")
	
			_delete_live_input(self.token, self.config["serviceApiUrl"], LIVE_INPUT_ID, 
								self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Delete live input complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete live input failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a live input.
	Parameters:
	LIVE_INPUT_ID (str): The ID of the live input.
	Returns:
	dict: The information of the live input.
	Exception: If the API type is not admin.
	Exception: If the get live input fails.
	"""
	def get_live_input(self, LIVE_INPUT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live input", sep=" ")

			LIVE_CHANNEL_INFO = _get_live_input(self.token, self.config["serviceApiUrl"], 
				LIVE_INPUT_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live input complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live input failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets all the live inputs.
	Returns:
	dict: The information of the live inputs.
	Exception: If the API type is not admin.
	Exception: If the get live inputs fails.
	"""
	def get_live_inputs(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live inputs", sep=" ")

			LIVE_CHANNEL_INFO = _get_live_inputs(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live inputs complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live inputs failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a live input.
	Parameters:
	LIVE_INPUT_ID (str): The ID of the live input.
	NAME (str | None): The name of the live input.
	SOURCE (str | None): The souce of the live input.
	TYPE (str | None): The type of the live input. The types are RTMP_PULL, RTMP_PUSH,
	RTP_PUSH, UDP_PUSH and URL_PULL
	IS_STANDARD (bool | None): Indicates if the live input is standard.
	VIDEO_ASSET_ID (str | None): The video asset ID of the live input.
	DESTINATIONS (list[dict] | None): The destinations of the live input. Sources must be URLs and are
	only valid for input types: RTMP_PUSH, URL_PULL, and MP4_FILE.
	dict format: {"ip": "string | None", "port": "string | None", "url": "string | None"}
	SOURCES (list[dict] | None): The sources of the live input. Sources must be URLs and are
	only valid for input types: RTMP_PULL.
	dict format: {"ip": "string | None", "port": "string | None", "url": "string | None"}
	Returns:
	dict: The information of the live input.
	Exception: If the API type is not admin.
	Exception: If the update live input fails.
	"""
	def update_live_input(self, LIVE_INPUT_ID: str, NAME: str | None, SOURCE: str | None, 
					      TYPE: str | None, IS_STANDARD: bool | None, VIDEO_ASSET_ID: str | None, 
						  DESTINATIONS: List[dict] | None, SOURCES: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start update live input", sep=" ")

			LIVE_CHANNEL_INFO = _update_live_input(self.token, self.config["serviceApiUrl"], 
				LIVE_INPUT_ID, NAME, SOURCE, TYPE, IS_STANDARD, VIDEO_ASSET_ID, DESTINATIONS, 
				SOURCES, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update live input complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update live input failed", sep=" ")
			raise Exception(error.args[0])
		
	# Live Operator
	"""
	Description:
	Cancels a broadcast.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the cancel broadcast fails.
	"""
	def cancel_broadcast(self, LIVE_OPERATOR_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start cancel broadcast", sep=" ")

			_cancel_broadcast(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Cancel broadcast complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Cancel broadcast failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Cancels a segment.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the cancel segment fails.
	"""
	def cancel_segment(self, LIVE_OPERATOR_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start cancel segment", sep=" ")

			_cancel_segment(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Cancel segment complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Cancel segment failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Completes a segment.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	RELATED_CONTENT_IDS (list | None): The related content IDs of the live operator.
	TAG_IDS (list | None): The tag IDs of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the complete segment fails.
	"""
	def complete_segment(self, LIVE_OPERATOR_ID: str, RELATED_CONTENT_IDS: List[str] | None, 
					     TAG_IDS: List[str] | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start complete segment", sep=" ")

			_complete_segment(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				RELATED_CONTENT_IDS, TAG_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Complete segment complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Complete segment failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets completed segments for given id.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	dict: The information of the completed segments.
	Exception: If the API type is not admin.
	Exception: If the get completed segment fails.
	"""
	def get_completed_segments(self, LIVE_OPERATOR_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get completed segments", sep=" ")

			LIVE_CHANNEL_INFO = _get_completed_segments(self.token, self.config["serviceApiUrl"], 
				LIVE_OPERATOR_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get completed segments complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get completed segments failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the live operator.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	dict: The information of the live operator.
	Exception: If the API type is not admin.
	Exception: If the get live operator fails.
	"""
	def get_live_operator(self, LIVE_OPERATOR_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live operator", sep=" ")

			LIVE_CHANNEL_INFO = _get_live_operator(self.token, self.config["serviceApiUrl"], 
				LIVE_OPERATOR_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live operator complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live operator failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets all the live operators.
	Returns:
	dict: The information of the live operators.
	Exception: If the API type is not admin.
	Exception: If the get live operators fails.
	"""
	def get_live_operators(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live operators", sep=" ")

			LIVE_CHANNEL_INFO = _get_live_operators(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live operators complete", sep=" ")

			return LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live operators failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
    Description:
	Starts a broadcast.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	PREROLL_ASSET_ID (str | None): The preroll asset ID of the live operator.
	POSTROLL_ASSET_ID (str | None): The postroll asset ID of the live operator.
	LIVE_INPUT_ID (str | None): The live input ID of the live operator.
	RELATED_CONTENT_IDS (list | None): The related content IDs of the live operator.
	TAG_IDS (list | None): The tag IDs of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the start broadcast fails.
	"""
	def start_broadcast(self, LIVE_OPERATOR_ID: str, PREROLL_ASSET_ID: str | None, 
					 	POSTROLL_ASSET_ID: str | None, LIVE_INPUT_ID: str | None, 
						RELATED_CONTENT_IDS: List[str] | None, TAG_IDS: List[str] | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start start broadcast", sep=" ")
	
			START_BROADCAST_INFO = _start_broadcast(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				PREROLL_ASSET_ID, POSTROLL_ASSET_ID, LIVE_INPUT_ID, RELATED_CONTENT_IDS, TAG_IDS, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Start broadcast complete", sep=" ")

			return START_BROADCAST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Start broadcast failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Starts a segment.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the start segment fails.
	"""
	def start_segment(self, LIVE_OPERATOR_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start start segment", sep=" ")
	
			_start_segment(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Start segment complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Start segment failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Stops Broadcast.
	Parameters:
	LIVE_OPERATOR_ID (str): The ID of the live operator.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the stop broadcast fails.
	"""
	def stop_broadcast(self, LIVE_OPERATOR_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start stop broadcast", sep=" ")
	
			_stop_broadcast(self.token, self.config["serviceApiUrl"], LIVE_OPERATOR_ID, 
				self.debug_mode)
	
			print(datetime.now().strftime('%H:%M:%S'), "Stop broadcast complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Stop broadcast failed", sep=" ")
			raise Exception(error.args[0])
		
	# Live Output Profile
	"""
	Description:
	Creates a live output profile.
	Parameters:
	NAME (str): The name of the live output profile.
	OUTPUT_TYPE (list | None): The type of the live output profile. Default is MediaStore.
	"MediaStore":"ac5146ea-4c01-4278-8c7b-0117f70c0100", Archive":"ac5146ea-4c01-4278-8c7b-0117f70c0200",  
    "MediaPackage":"ac5146ea-4c01-4278-8c7b-0117f70c0300", "Rtmp":"ac5146ea-4c01-4278-8c7b-0117f70c0400",  
    "S3":"ac5146ea-4c01-4278-8c7b-0117f70c0500", "LiveVodHls":"ac5146ea-4c01-4278-8c7b-0117f70c0600",  
    "Rtp":"ac5146ea-4c01-4278-8c7b-0117f70c0700", "RtpFec":"ac5146ea-4c01-4278-8c7b-0117f70c0800"* 
    Dict format: {"name": "string", "id": "string"} 
	ENABLED (bool | None): Indicates if the live output profile is enabled.
	AUDIO_BITRATE (int | None): The audio bitrate of the live output profile.
	The audio bitrate in bytes. For example, 128KB = 128000.
	OUTPUT_STREAM_KEY (str | None): The output stream key of the live output profile.
	OUTPUT_URL (str | None): The output URL of the live output profile.
	SECONDARY_OUTPUT_STREAM_KEY (str | None): The secondary output stream key of the live output profile.
	SECONDARY_URL (str | None): The secondary URL of the live output profile.
	VIDEO_BITRATE (int | None): The video bitrate of the live output profile.
	The video bitrate in bytes. For example, 2mbps = 2048000, validate > 0.
	VIDEO_BITRATE_MODE (str | None): The video bitrate mode of the live output profile. The modes are CBR and VBR.
	VIDEO_CODEC (str | None): The video codec of the live output profile. The codecs are H264 and H265.
	VIDEO_FRAMES_PER_SECOND (int | None): The video frames per second of the live output profile.
	VIDEO_HEIGHT (int | None): The video height of the live output profile.
	VIDEO_WIDTH (int | None): The video width of the live output profile.
	Returns:
	list[dict]: The information of the live output profile.
	Exception: If the API type is not admin.
	Exception: If the create live output profile fails.
	"""
	def create_live_output_profile(self, NAME: str, OUTPUT_TYPE: str | None, ENABLED: bool | None,
						   AUDIO_BITRATE: int | None, OUTPUT_STREAM_KEY: str | None,
						   OUTPUT_URL: str | None, SECONDARY_OUTPUT_STREAM_KEY: str | None,
						   SECONDARY_URL: str | None, VIDEO_BITRATE: int | None, 
						   VIDEO_BITRATE_MODE: str | None, VIDEO_CODEC: str | None, 
						   VIDEO_FRAMES_PER_SECOND: int | None, VIDEO_HEIGHT: int | None, 
						   VIDEO_WIDTH: int | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start create live output profile", sep=" ")

			LIVE_OUTPUT_INFO = _create_live_output_profile(self.token, self.config["serviceApiUrl"], 
				NAME, OUTPUT_TYPE, ENABLED, AUDIO_BITRATE, OUTPUT_STREAM_KEY, OUTPUT_URL, 
				SECONDARY_OUTPUT_STREAM_KEY, SECONDARY_URL, VIDEO_BITRATE, VIDEO_BITRATE_MODE, 
				VIDEO_CODEC, VIDEO_FRAMES_PER_SECOND, VIDEO_HEIGHT, VIDEO_WIDTH, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create live output profile complete", sep=" ")

			return LIVE_OUTPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create live output profile failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a live output profile.
	Parameters:
	LIVE_OUTPUT_ID (str): The ID of the live output profile.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the delete live output profile fails.
	"""
	def delete_live_output_profile(self, LIVE_OUTPUT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start delete live output profile", sep=" ")

			_delete_live_output_profile(self.token, self.config["serviceApiUrl"], LIVE_OUTPUT_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete live output profile complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete live output profile failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a live output profile.
	Parameters:
	LIVE_OUTPUT_ID (str): The ID of the live output profile.
	Returns:
	dict: The information of the live output profile.
	Exception: If the API type is not admin.
	Exception: If the get live output profile fails.
	"""
	def get_live_output_profile(self, LIVE_OUTPUT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live output profile", sep=" ")

			LIVE_OUTPUT_INFO = _get_live_output_profile(self.token, self.config["serviceApiUrl"], 
				LIVE_OUTPUT_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile complete", sep=" ")

			return LIVE_OUTPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets all the live output profiles
	Returns:
	list[dict]: The information of the live output profiles.
	Exception: If the API type is not admin.
	Exception: If the get live output profiles fails.
	"""
	def get_live_output_profiles(self) -> list[dict]:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live outputs", sep=" ")

			LIVE_OUTPUT_INFO = _get_live_output_profiles(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live outputs complete", sep=" ")

			return LIVE_OUTPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live outputs failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets live output types
	Returns:
	dict: The information of the live output types.
	Exception: If the API type is not admin.
	Exception: If the get live output types fails.
	"""
	def get_live_output_types(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live output types", sep=" ")

			LIVE_OUTPUT_INFO = _get_live_output_types(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live output types complete", sep=" ")

			return LIVE_OUTPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live output types failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates a live output profile.
	Parameters:
	LIVE_OUTPUT_ID (str): The ID of the live output profile.
	NAME (str | None): The name of the live output profile.
	OUTPUT_TYPE (list | None): The type of the live output profile. Default is MediaStore.
	"MediaStore":"ac5146ea-4c01-4278-8c7b-0117f70c0100", Archive":"ac5146ea-4c01-4278-8c7b-0117f70c0200",  
    "MediaPackage":"ac5146ea-4c01-4278-8c7b-0117f70c0300", "Rtmp":"ac5146ea-4c01-4278-8c7b-0117f70c0400",  
    "S3":"ac5146ea-4c01-4278-8c7b-0117f70c0500", "LiveVodHls":"ac5146ea-4c01-4278-8c7b-0117f70c0600",  
    "Rtp":"ac5146ea-4c01-4278-8c7b-0117f70c0700", "RtpFec":"ac5146ea-4c01-4278-8c7b-0117f70c0800"* 
    Dict format: {"name": "string", "id": "string"} 
	ENABLED (bool | None): Indicates if the live output profile is enabled.
	AUDIO_BITRATE (int | None): The audio bitrate of the live output profile.
	OUTPUT_STREAM_KEY (str | None): The output stream key of the live output profile.
	OUTPUT_URL (str | None): The output URL of the live output profile.
	SECONDARY_OUTPUT_STREAM_KEY (str | None): The secondary output stream key of the live output profile.
	SECONDARY_URL (str | None): The secondary URL of the live output profile.
	VIDEO_BITRATE (int | None): The video bitrate of the live output profile.
	VIDEO_BITRATE_MODE (str | None): The video bitrate mode of the live output profile. The modes are CBR and VBR.
	VIDEO_CODEC (str | None): The video codec of the live output profile. The codecs are H264 and H265.
	VIDEO_FRAMES_PER_SECOND (int | None): The video frames per second of the live output profile.
	VIDEO_HEIGHT (int | None): The video height of the live output profile.
	VIDEO_WIDTH (int | None): The video width of the live output profile.
	Returns:
	dict: The information of the live output profile.
	Exception: If the API type is not admin.
	Exception: If the update live output profile fails.
	"""
	def update_live_output_profile(self, LIVE_OUTPUT_ID: str, NAME: str | None, OUTPUT_TYPE: str | None,
						   ENABLED: bool | None, AUDIO_BITRATE: int | None, 
						   OUTPUT_STREAM_KEY: str | None, OUTPUT_URL: str | None, 
						   SECONDARY_OUTPUT_STREAM_KEY: str | None, SECONDARY_URL: str | None, 
						   VIDEO_BITRATE: int | None, VIDEO_BITRATE_MODE: str | None, 
						   VIDEO_CODEC: str | None, VIDEO_FRAMES_PER_SECOND: int | None, 
						   VIDEO_HEIGHT: int | None, VIDEO_WIDTH: int | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start update live output profile", sep=" ")

			LIVE_OUTPUT_INFO = _update_live_output_profile(self.token, self.config["serviceApiUrl"], 
				LIVE_OUTPUT_ID, NAME, OUTPUT_TYPE, ENABLED, AUDIO_BITRATE, OUTPUT_STREAM_KEY, 
				OUTPUT_URL, SECONDARY_OUTPUT_STREAM_KEY, SECONDARY_URL, VIDEO_BITRATE, 
				VIDEO_BITRATE_MODE, VIDEO_CODEC, VIDEO_FRAMES_PER_SECOND, VIDEO_HEIGHT, 
				VIDEO_WIDTH, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update live output profile complete", sep=" ")

			return LIVE_OUTPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update live output profile failed", sep=" ")
			raise Exception(error.args[0])

	# Live Output Profile Group
	"""
	Description:
	Creates a live output profile group.
	Parameters:
	NAME (str): The name of the live output profile group.
	IS_ENABLED (bool): Indicates if the live output profile group is enabled.
	MANIFEST_TYPE (str): The manifest type of the live output profile group. The types are HLS, DASH, and BOTH.
	IS_DEFAULT_GROUP (bool): Indicates if the live output profile group is the default group.
	LIVE_OUTPUT_TYPE (list | None): The type of the live output profile. Default is MediaStore.
	"MediaStore":"ac5146ea-4c01-4278-8c7b-0117f70c0100", Archive":"ac5146ea-4c01-4278-8c7b-0117f70c0200",  
    "MediaPackage":"ac5146ea-4c01-4278-8c7b-0117f70c0300", "Rtmp":"ac5146ea-4c01-4278-8c7b-0117f70c0400",  
    "S3":"ac5146ea-4c01-4278-8c7b-0117f70c0500", "LiveVodHls":"ac5146ea-4c01-4278-8c7b-0117f70c0600",  
    "Rtp":"ac5146ea-4c01-4278-8c7b-0117f70c0700", "RtpFec":"ac5146ea-4c01-4278-8c7b-0117f70c0800"* 
    Dict format: {"name": "string", "id": "string"} LIVE_OUTPUT_TYPE (list): The type of the live output profile group.
	dict format: {"description": "string", "id": "string"}
	ARCHIVE_LIVE_OUTPUT_PROFILE (list | None): The archive live output profile of the live output profile group.
	dict format: {"description": "string", "id": "string"}
	LIVE_OUTPUT_PROFILES (list): The live output profile of the live output profile group.
	Returns:
	dict: The information of the live output profile group.
	Exception: If the API type is not admin.
	Exception: If the create live output profile group fails.
	"""
	def create_live_output_profile_group(self, NAME: str, IS_ENABLED: bool, MANIFEST_TYPE: str,
										 IS_DEFAULT_GROUP: bool, LIVE_OUTPUT_TYPE: list,
										 ARCHIVE_LIVE_OUTPUT_PROFILE: list | None, LIVE_OUTPUT_PROFILES: list) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start create live output profile group", sep=" ")

			LIVE_OUTPUT_PROFILE_GROUP_INFO = _create_live_output_profile_group(self.token, 
				self.config["serviceApiUrl"], NAME, IS_ENABLED, MANIFEST_TYPE, IS_DEFAULT_GROUP, 
				LIVE_OUTPUT_TYPE, ARCHIVE_LIVE_OUTPUT_PROFILE, LIVE_OUTPUT_PROFILES, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create live output profile group complete", sep=" ")

			return LIVE_OUTPUT_PROFILE_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create live output profile group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a live output profile group.
	Parameters:
	LIVE_OUTPUT_PROFILE_GROUP_ID (str): The ID of the live output profile group.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the delete live output profile group fails.
	"""
	def delete_live_output_profile_group(self, LIVE_OUTPUT_PROFILE_GROUP_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start delete live output profile group", sep=" ")

			_delete_live_output_profile_group(self.token, self.config["serviceApiUrl"], 
				LIVE_OUTPUT_PROFILE_GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete live output profile group complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete live output profile group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a live output profile group.
	Parameters:
	LIVE_OUTPUT_PROFILE_GROUP_ID (str): The ID of the live output profile group.
	Returns:
	dict: The information of the live output profile group.
	Exception: If the API type is not admin.
	Exception: If the get live output profile group fails.
	"""
	def get_live_output_profile_group(self, LIVE_OUTPUT_PROFILE_GROUP_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live output profile group", sep=" ")

			LIVE_OUTPUT_PROFILE_GROUP_INFO = _get_live_output_profile_group(self.token, 
				self.config["serviceApiUrl"], LIVE_OUTPUT_PROFILE_GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile group complete", sep=" ")

			return LIVE_OUTPUT_PROFILE_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets all the live output profile groups.
	Returns:
	dict: The information of the live output profile groups.
	Exception: If the API type is not admin.
	Exception: If the get live output profile groups fails.
	"""
	def get_live_output_profile_groups(self) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get live output profile groups", sep=" ")

			LIVE_OUTPUT_PROFILE_GROUP_INFO = _get_live_output_profile_groups(self.token, 
				self.config["serviceApiUrl"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile groups complete", sep=" ")

			return LIVE_OUTPUT_PROFILE_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get live output profile groups failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a live output profile group.
	Parameters:
	LIVE_OUTPUT_PROFILE_GROUP_ID (str): The ID of the live output profile group.
	NAME (str | None): The name of the live output profile group.
	IS_ENABLED (bool | None): Indicates if the live output profile group is enabled.
	MANIFEST_TYPE (str | None): The manifest type of the live output profile group.
	IS_DEFAULT_GROUP (bool | None): Indicates if the live output profile group is the default group.
	LIVE_OUTPUT_TYPE (list | None): The type of the live output profile. Default is MediaStore.
	"MediaStore":"ac5146ea-4c01-4278-8c7b-0117f70c0100", Archive":"ac5146ea-4c01-4278-8c7b-0117f70c0200",  
    "MediaPackage":"ac5146ea-4c01-4278-8c7b-0117f70c0300", "Rtmp":"ac5146ea-4c01-4278-8c7b-0117f70c0400",  
    "S3":"ac5146ea-4c01-4278-8c7b-0117f70c0500", "LiveVodHls":"ac5146ea-4c01-4278-8c7b-0117f70c0600",  
    "Rtp":"ac5146ea-4c01-4278-8c7b-0117f70c0700", "RtpFec":"ac5146ea-4c01-4278-8c7b-0117f70c0800"* 
    Dict format: {"name": "string", "id": "string"} 
	ARCHIVE_LIVE_OUTPUT_PROFILE (list | None): The archive live output profile of the live output profile group.
	dict format: {"description": "string", "id": "string"}
	LIVE_OUTPUT_PROFILE (list | None): The live output profile of the live output profile group.
	Returns:
	dict: The information of the live output profile group.
	Exception: If the API type is not admin.
	Exception: If the update live output profile group fails.
	"""
	def update_live_output_profile_group(self, LIVE_OUTPUT_PROFILE_GROUP_ID: str, NAME: str | None,
										 IS_ENABLED: bool | None, MANIFEST_TYPE: str | None,
										 IS_DEFAULT_GROUP: bool | None, LIVE_OUTPUT_TYPE: list | None,
										 ARCHIVE_LIVE_OUTPUT_PROFILE: list | None,
										 LIVE_OUTPUT_PROFILE: list | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start update live output profile group", sep=" ")

			LIVE_OUTPUT_PROFILE_GROUP_INFO = _update_live_output_profile_group(self.token, 
				self.config["serviceApiUrl"], LIVE_OUTPUT_PROFILE_GROUP_ID, NAME, IS_ENABLED, 
				MANIFEST_TYPE, IS_DEFAULT_GROUP, LIVE_OUTPUT_TYPE, ARCHIVE_LIVE_OUTPUT_PROFILE, 
				LIVE_OUTPUT_PROFILE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update live output profile group complete", sep=" ")

			return LIVE_OUTPUT_PROFILE_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update live output profile group failed", sep=" ")
			raise Exception(error.args[0])
	
	# Schedule Event
	"""
	Description:
	Adds an asset schedule event to a live channel.
	Paremeters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	ASSET (dict): The asset of the asset schedule event.
	IS_LOOP (bool): Indicates if the asset schedule event should loop.
	DURATION_TIME_CODE (str | None): The duration time code of the asset schedule event.
	Please use the following format: HH:MM:SS;FF
	PREVIOUS_ID (str | None): The ID of the previous asset schedule event.
	Returns:
	dict: The information of the asset schedule event.
	Exception: If the API type is not admin.
	Exception: If the adding asset schedule event fails.
	"""
	def add_asset_schedule_event(self, LIVE_CHANNEL_ID: str, ASSET: dict, IS_LOOP: bool, 
							  	 DURATION_TIME_CODE: str | None, PREVIOUS_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Add asset schedule event", sep=" ")

			ASSET_INFO = _add_asset_schedule_event(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				ASSET, IS_LOOP, DURATION_TIME_CODE, PREVIOUS_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Add asset schedule event complete", sep=" ")

			return ASSET_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add asset schedule event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Adds a live input schedule event to a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	LIVE_INPUT (dict): The live input of the live input schedule event.
	BACKUP_LIVE_INPUT (dict): The backup live input of the live input schedule event.
	FIXED_ON_AIR_TIME_UTC (str | None): The fixed on air time UTC of the live input schedule event.
	Please use the following format: HH:MM:SS
	PREVIOUS_ID (str | None): The ID of the previous live input schedule event.
	Returns:
	dict: The information of the live input schedule event.
	Exception: If the API type is not admin.
	Exception: If the adding live input schedule event fails.
	"""
	def add_input_schedule_event(self, LIVE_CHANNEL_ID: str, LIVE_INPUT: dict, 
								   	  BACKUP_LIVE_INPUT: dict, FIXED_ON_AIR_TIME_UTC: str | None, 
									  PREVIOUS_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Add live input schedule event", sep=" ")

			LIVE_INPUT_INFO = _add_input_schedule_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, LIVE_INPUT, BACKUP_LIVE_INPUT, FIXED_ON_AIR_TIME_UTC, 
				PREVIOUS_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Add live input schedule event complete", sep=" ")

			return LIVE_INPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add live input schedule event failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets an asset schedule event.
	Parameters:
	CHANNEL_ID (str): The channel ID of the schedule event.
	SCHEDULE_EVENT_ID (str): The schedule event ID of the schedule event.
	Returns:
	dict: Returns the information of the gotten asset schedule event.
	Exception: An error is thrown if the asset schedule event fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_asset_schedule_event(self, LIVE_CHANNEL_ID: str, SCHEDULE_EVENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Get asset schedule event", sep=" ")

			ASSET_INFO = _get_asset_schedule_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, SCHEDULE_EVENT_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Get asset schedule event complete", sep=" ")

			return ASSET_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get asset schedule event failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets an input schedule event.
	Parameters:
	CHANNEL_ID (str): The channel ID of the schedule event.
	SCHEDULE_EVENT_ID (str): The schedule event ID of the schedule event.
	Returns:
	dict: Returns the information of the gotten asset schedule event.
	Exception: An error is thrown if the asset schedule event fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_input_schedule_event(self, LIVE_CHANNEL_ID: str, SCHEDULE_EVENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Get input schedule event", sep=" ")

			INPUT_INFO = _get_input_schedule_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, SCHEDULE_EVENT_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get input schedule event complete", sep=" ")

			return INPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get input schedule event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Moves a schedule event.
	Parameters:
	CHANNEL_ID (str): The channel ID of the schedule event.
	SCHEDULE_EVENT_ID (str): The schedule event ID of the schedule event.
	PREVIOUS_SCHEDULE_EVENT_ID (str | None): The previous schedule event ID of the schedule event.
	Returns:
	dict: Returns the information of the moved schedule event.
	Exception: An error is thrown if the schedule event fails to move.
	Exception: An error is thrown if the API type is not admin.
	"""
	def move_schedule_event(self, LIVE_CHANNEL_ID: str, SCHEDULE_EVENT_ID: str, 
							PREVIOUS_SCHEDULE_EVENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Move schedule event", sep=" ")

			_move_schedule_event(self.token, self.config["serviceApiUrl"], LIVE_CHANNEL_ID, 
				SCHEDULE_EVENT_ID, PREVIOUS_SCHEDULE_EVENT_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Move schedule event complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Move schedule event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Removes a live asset schedule event from a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	SCHEDULE_EVENT_ID (str): The ID of the schedule event.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If removing asset schedule event fails.
	"""
	def remove_asset_schedule_event(self, LIVE_CHANNEL_ID: str, SCHEDULE_EVENT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Remove asset schedule event", sep=" ")

			_remove_asset_schedule_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, SCHEDULE_EVENT_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Remove asset schedule event complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add live operator schedule event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Removes a live input schedule event from a live channel.
	Parameters:
	LIVE_CHANNEL_ID (str): The ID of the live channel.
	INPUT_ID (str): The ID of the schedule event.
	Returns:
	None
	Exception: If the API type is not admin.
	Exception: If the removing input schedule event fails.
	"""
	def remove_input_schedule_event(self, LIVE_CHANNEL_ID: str, INPUT_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Remove input schedule event", sep=" ")

			_remove_input_schedule_event(self.token, self.config["serviceApiUrl"], 
				LIVE_CHANNEL_ID, INPUT_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Remove input schedule event complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add live operator schedule event failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates an asset schedule event.
	Parameters:
	ID (str): The ID of the schedule event.
	CHANNEL_ID (str): The channel ID of the schedule event.
	ASSET (dict | None): The asset of the schedule event. Format: {"id": "string", "name": "string"}
	IS_LOOP (bool | None): Whether the schedule event is loop.
	DURATION_TIME_CODE (str | None): The duration time code of the schedule event. Please use the following format: hh:mm:ss;ff. Set to null if IS_LOOP is true.
	Returns:
	dict: Returns the information of the added asset schedule event.
	Exception: An error is thrown if the asset schedule event fails to add.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_asset_schedule_event(self, ID: str, CHANNEL_ID: str, ASSET: dict, IS_LOOP: bool, 
									DURATION_TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Update asset schedule event", sep=" ")

			ASSET_INFO = _update_asset_schedule_event(self.token, self.config["serviceApiUrl"], 
				ID, CHANNEL_ID, ASSET, IS_LOOP, DURATION_TIME_CODE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update asset schedule event complete", sep=" ")

			return ASSET_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update asset schedule event failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates an input schedule event.
	Parameters:
	ID (str): The ID of the Input schedule event.
	CHANNEL_ID (str): The channel ID of the schedule event.
	INPUT (dict | None): The input of the schedule event. Format: {"id": "string", "name": "string"}
	BACKUP_INPUT (dict, None): The backup input of the schedule event. Format: {"id": "string", "name": "string"}
	FIXED_ON_AIR_TIME_UTC (str, None): The fixed on air time UTC of the schedule event. Please use the following format: hh:mm:ss.
	Returns:
	dict: Returns the information of the added input schedule event.
	Exception: An error is thrown if the input schedule event fails to add.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_input_schedule_event(self, ID: str, CHANNEL_ID: str, INPUT: dict,
									BACKUP_INPUT: dict | None, FIXED_ON_AIR_TIME_UTC: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Update input schedule event", sep=" ")

			INPUT_INFO = _update_input_schedule_event(self.token, self.config["serviceApiUrl"], 
				ID, CHANNEL_ID, INPUT, BACKUP_INPUT, FIXED_ON_AIR_TIME_UTC, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update input schedule event complete", sep=" ")

			return INPUT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update input schedule event failed", sep=" ")
			raise Exception(error.args[0])									

	# Schedule
	"""
	Description:
	Creates an intelligent playlist.
	Parameters:
	COLLECTIONS (list[dict], None): The collections of the intelligent playlist. Format: {"id": "string", "description": "string"}
	END_SEARCH_DATE (str, None): The end search date of the intelligent playlist. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	END_SEARCH_DURATION_IN_MINUTES (int): The end search duration in minutes of the intelligent playlist.
	NAME (str): The name of the intelligent playlist.
	RELATED_CONTENTS (list[dict], None): The related content of the intelligent playlist. Format: {"id": "string", "description": "string"}
	SEARCH_DATE (str, None): The search date of the intelligent playlist. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	SEARCH_DURATION_IN_MINUTES (int): The search duration in minutes of the intelligent playlist.
	SEARCH_FILTER_TYPE (int): The search filter type of the intelligent playlist. Values: Random: 1, Random within a Date Range: 2, Newest: 3, Newest Not Played: 4
	TAGS (list[dict]): The tags of the intelligent playlist. Format: {"id": "string", "description": "string"}
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the intelligent playlist. Format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the created intelligent playlist.
	Exception: An error is thrown if the intelligent playlist fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_intelligent_playlist(self, COLLECTIONS: List[dict] | None, END_SEARCH_DATE: str | None,
									END_SEARCH_DURATION_IN_MINUTES: int, NAME: str, 
									RELATED_CONTENTS: List[dict] | None, SEARCH_DATE: str | None,
									SEARCH_DURATION_IN_MINUTES: int, SEARCH_FILTER_TYPE: int,
									TAGS: List[dict], THUMBNAIL_ASSET: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating intelligent playlist", sep=" ")

			INTELLIGENT_PLAYLIST_INFO = _create_intelligent_playlist(self.token, self.config["serviceApiUrl"], 
				COLLECTIONS, END_SEARCH_DATE, END_SEARCH_DURATION_IN_MINUTES, NAME, 
				RELATED_CONTENTS, SEARCH_DATE, SEARCH_DURATION_IN_MINUTES, SEARCH_FILTER_TYPE,
				TAGS, THUMBNAIL_ASSET, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Intelligent playlist created", sep=" ")

			return INTELLIGENT_PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create intelligent playlist failed", sep=" ")
			raise Exception(error.args[0])		

	"""
	Description:
	Creates an intelligent schedule.
	Parameters:
	DEFAULT_VIDEO_ASSET (dict): The default video asset of the intelligent schedule. Format: {"id": "string", "description": "string"}
	NAME (str): The name of the intelligent schedule.
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the intelligent schedule. Format: {"id": "string", "description": "string"}
	TIME_ZONE_ID (str | None): The time zone ID of the intelligent schedule.
	Returns:
	dict: Returns the information of the created intelligent schedule.
	Exception: An error is thrown if the intelligent schedule fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_intelligent_schedule(self, DEFAULT_VIDEO_ASSET: dict, NAME: str, 
									THUMBNAIL_ASSET: dict | None, TIME_ZONE_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating intelligent schedule", sep=" ")

			INTELLIGENT_SCHEDULE_INFO = _create_intelligent_schedule(self.token, self.config["serviceApiUrl"], 
				DEFAULT_VIDEO_ASSET, NAME, THUMBNAIL_ASSET, TIME_ZONE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent schedule created", sep=" ")

			return INTELLIGENT_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create intelligent schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a playlist.
	Parameters:
	NAME (str): The name of the playlist.
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the playlist. Format: {"id": "string", "description": "string"}
	LOOP_PLAYLIST (bool): Whether the playlist is looped.
	DEFAULT_VIDEO_ASSET (dict): The default video asset of the playlist. Format: {"id": "string"}. Only needed if LOOP_PLAYLIST is false.
	Returns:
	dict: Returns the information of the created playlist.
	Exception: An error is thrown if the playlist fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_playlist(self, NAME: str, THUMBNAIL_ASSET: dict | None, LOOP_PLAYLIST: bool,
						DEFAULT_VIDEO_ASSET: dict) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating playlist", sep=" ")

			PLAYLIST_INFO = _create_playlist(self.token, self.config["serviceApiUrl"], 
				NAME, THUMBNAIL_ASSET, LOOP_PLAYLIST, DEFAULT_VIDEO_ASSET, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Playlist created", sep=" ")

			return PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create playlist failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a playlist video.
	Parameters:
	PLAYLIST_ID (str): The ID of the playlist.
	VIDEO_ASSET (dict): The video asset of the playlist video. Format: {"id": "string", "description": "string"}
	PREVIOUS_ITEM (str, None): The previous item of the playlist video.
	Returns:
	dict: Returns the information of the created playlist video.
	Exception: An error is thrown if the playlist video fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_playlist_video(self, PLAYLIST_ID: str, VIDEO_ASSET: dict, PREVIOUS_ITEM: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating playlist video", sep=" ")

			PLAYLIST_VIDEO_INFO = _create_playlist_video(self.token, self.config["serviceApiUrl"], 
				PLAYLIST_ID, VIDEO_ASSET, PREVIOUS_ITEM, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Playlist video created", sep=" ")

			return PLAYLIST_VIDEO_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create playlist video failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a schedule item asset.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the asset item is to be added to.
	ASSET (dict): The asset of the schedule item asset. Format: {"id": "string"}
	DAYS (list[dict]): The days of the schedule item asset. Format: {"id": "string"}
	DURATION_TIME_CODE (str): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str): The end time code of the schedule item asset. Please use the following format: hh:mm:ss;ff.
	PREVIOUS_ITEM (str, None): The previous item of the schedule item asset.
	TIME_CODE (str): The time code of the schedule item asset. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the created schedule item asset.
	Exception: An error is thrown if the schedule item asset fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_schedule_item_asset(self, SCHEDULE_ID: str, ASSET: dict, DAYS: List[dict],
								   DURATION_TIME_CODE: str, END_TIME_CODE: str, 
								   PREVIOUS_ITEM: str | None, TIME_CODE: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating schedule item asset", sep=" ")

			SCHEDULE_ITEM_ASSET_INFO = _create_schedule_item_asset(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ASSET, DAYS, DURATION_TIME_CODE, END_TIME_CODE, PREVIOUS_ITEM, TIME_CODE, 
				self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Schedule item asset created", sep=" ")

			return SCHEDULE_ITEM_ASSET_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create schedule item asset failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a schedule item live channel.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the live channel item is to be added to.
	DAYS (list[dict]): The days of the schedule item live channel. Format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str): The end time code of the schedule item live channel. Please use the following format: hh:mm:ss;ff.
	LIVE_CHANNEL (dict): The live channel of the schedule item live channel. Format: {"id": "string", "description": "string"}. Note: The live channel must be non-secure output.
	PREVIOUS_ITEM (str, None): The previous item of the schedule item live channel.
	TIME_CODE (str): The time code of the schedule item live channel.
	Returns:
	dict: Returns the information of the created schedule item live channel.
	Exception: An error is thrown if the schedule item live channel fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_schedule_item_live_channel(self, SCHEDULE_ID: str, DAYS: List[dict],
										  DURATION_TIME_CODE: str, END_TIME_CODE: str, 
										  LIVE_CHANNEL: dict, PREVIOUS_ITEM: str | None, 
										  TIME_CODE: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating schedule item live channel", sep=" ")

			SCHEDULE_ITEM_LIVE_CHANNEL_INFO = _create_schedule_item_live_channel(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, DAYS, DURATION_TIME_CODE, END_TIME_CODE, LIVE_CHANNEL, PREVIOUS_ITEM, 
				TIME_CODE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item live channel created", sep=" ")

			return SCHEDULE_ITEM_LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create schedule item live channel failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a schedule item playlist schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the playlist schedule item is to be added to.
	DAYS (list[dict]): The days of the schedule item playlist schedule. Format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str): The end time code of the schedule item playlist schedule. Please use the following format: hh:mm:ss;ff.
	PLAYLIST_SCHEDULE (dict): The playlist schedule of the schedule item playlist schedule. Format: {"id": "string", "description": "string"}
	PREVIOUS_ITEM (str, None): The previous item of the schedule item playlist schedule.
	TIME_CODE (str): The time code of the schedule item playlist schedule. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the created schedule item playlist schedule.
	Exception: An error is thrown if the schedule item playlist schedule fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_schedule_item_playlist_schedule(self, SCHEDULE_ID: str, DAYS: List[dict],
											   DURATION_TIME_CODE: str, END_TIME_CODE: str, 
											   PLAYLIST_SCHEDULE: dict, PREVIOUS_ITEM: str | None,
											   TIME_CODE: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating schedule item playlist schedule", sep=" ")

			SCHEDULE_ITEM_PLAYLIST_SCHEDULE_INFO = _create_schedule_item_playlist_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, DAYS, DURATION_TIME_CODE, END_TIME_CODE, PLAYLIST_SCHEDULE, PREVIOUS_ITEM, 
				TIME_CODE, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Schedule item playlist schedule created", sep=" ")

			return SCHEDULE_ITEM_PLAYLIST_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create schedule item playlist schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a schedule item search filter.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the search filter item is to be added to.
	COLLECTIONS (list[dict], None): The collections of the schedule item search filter. Format: {"id": "string", "description": "string"}
	DAYS (list[dict]): The days of the schedule item search filter. Format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_SEARCH_DATE (str, None): The end search date of the schedule item search filter. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	END_SEARCH_DURATION_IN_MINUTES (int): The end search duration in minutes of the schedule item search filter.
	END_TIME_CODE (str): The end time code of the schedule item search filter. Please use the following format: hh:mm:ss;ff.
	PREVIOUS_ITEM (str, None): The previous item of the schedule item search filter.
	RELATED_CONTENTS (list[dict], None): The related contents of the schedule item search filter.
	SEARCH_DATE (str, None): The search date of the schedule item search filter. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	SEARCH_DURATION_IN_MINUTES (str): The search duration in minutes of the schedule item search filter.
	SEARCH_FILTER_TYPE (str): The search filter type of the schedule item search filter. Values: Random: 1, Random within a Date Range: 2, Newest: 3, Newest Not Played: 4
	TAGS (list[dict]): The tags of the schedule item search filter. Format: {"id": "string", "description": "string"}
	TIME_CODE (str): The time code of the schedule item search filter. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: 
	Exception: An error is thrown if the schedule item search filter fails to create.
	Exception: An error is thrown if the API type is not admin.
	"""
	def create_schedule_item_search_filter(self, SCHEDULE_ID: str, COLLECTIONS: List[dict] | None,
										   DAYS: List[dict], DURATION_TIME_CODE: str, 
										   END_SEARCH_DATE: str | None, 
										   END_SEARCH_DURATION_IN_MINUTES: int, 
										   END_TIME_CODE: str, PREVIOUS_ITEM: str | None,
										   RELATED_CONTENTS: List[dict] | None, 
										   SEARCH_DATE: str | None, SEARCH_DURATION_IN_MINUTES: int,
										   SEARCH_FILTER_TYPE: int, TAGS: List[dict], 
										   TIME_CODE: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Creating schedule item search filter", sep=" ")

			SCHEDULE_ITEM_SEARCH_FILTER_INFO = _create_schedule_item_search_filter(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, COLLECTIONS, DAYS, DURATION_TIME_CODE, END_SEARCH_DATE, 
				END_SEARCH_DURATION_IN_MINUTES, END_TIME_CODE, PREVIOUS_ITEM, RELATED_CONTENTS, 
				SEARCH_DATE, SEARCH_DURATION_IN_MINUTES, SEARCH_FILTER_TYPE, TAGS, TIME_CODE, 
				self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Schedule item search filter created", sep=" ")

			return SCHEDULE_ITEM_SEARCH_FILTER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create schedule item search filter failed", sep=" ")
			raise Exception(error.args[0])
	"""
	Description:
	Deletes an intelligent playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the intelligent playlist to be deleted.
	Returns:
	None: A promise that resolves when the intelligent playlist is deleted.
	Exception: An error is thrown if the intelligent playlist fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_intelligent_playlist(self, SCHEDULE_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting intelligent playlist", sep=" ")

			_delete_intelligent_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent playlist deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete intelligent playlist failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the intelligent schedule to be deleted.
	Returns:
	None: A promise that resolves when the intelligent schedule is deleted.
	Exception: An error is thrown if the intelligent schedule fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_intelligent_schedule(self, SCHEDULE_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting intelligent schedule", sep=" ")

			_delete_intelligent_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent schedule deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete intelligent schedule failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the playlist to be deleted.
	Returns:
	None: A promise that resolves when the playlist is deleted.
	Exception: An error is thrown if the playlist fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_playlist(self, SCHEDULE_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting playlist", sep=" ")

			_delete_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Playlist deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete playlist failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a schedule item.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item is to be deleted from.
	ITEM_ID (str): The id of the item to be deleted.
	Returns:
	None: A promise that resolves when the schedule item is deleted.
	Exception: An error is thrown if the schedule item fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_schedule_item(self, SCHEDULE_ID: str, ITEM_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting schedule item", sep=" ")

			_delete_schedule_item(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete schedule item failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets an intelligent playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the intelligent playlist to be gotten.
	Returns:
	dict: Returns the information of the gotten intelligent playlist.
	Exception: An error is thrown if the intelligent playlist fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_intelligent_playlist(self, SCHEDULE_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting intelligent playlist", sep=" ")

			INTELLIGENT_PLAYLIST_INFO = _get_intelligent_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Intelligent playlist gotten", sep=" ")

			return INTELLIGENT_PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get intelligent playlist failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets an intelligent schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the intelligent schedule to be gotten.
	Returns:
	dict: Returns the information of the gotten intelligent playlist.
	Exception: An error is thrown if the intelligent schedule fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_intelligent_schedule(self, SCHEDULE_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting intelligent schedule", sep=" ")

			INTELLIGENT_SCHEDULE_INFO = _get_intelligent_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent schedule gotten", sep=" ")

			return INTELLIGENT_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get intelligent schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the playlist to be gotten.
	Returns:
	dict: Returns the information of the gotten intelligent playlist.
	Exception: An error is thrown if the playlist fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_playlist(self, SCHEDULE_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting playlist", sep=" ")

			PLAYLIST_INFO = _get_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Playlist gotten", sep=" ")

			return PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get playlist failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a schedule item.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item is to be gotten from.
	ITEM_ID (str): The id of the item to be gotten.
	Returns:
	dict: Returns the information of the gotten schedule item.
	Exception: An error is thrown if the schedule item fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_schedule_item(self, SCHEDULE_ID: str, ITEM_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting schedule item", sep=" ")

			SCHEDULE_ITEM_INFO = _get_schedule_item(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item gotten", sep=" ")

			return SCHEDULE_ITEM_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get schedule item failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the schedule items of a schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule items are to be gotten from.
	Returns:
	list[dict]: Returns the information of the gotten schedule items.
	Exception: An error is thrown if the schedule items fail to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_schedule_items(self, SCHEDULE_ID: str) -> List[dict]:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting schedule items", sep=" ")

			SCHEDULE_ITEMS_INFO = _get_schedule_items(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Schedule items gotten", sep=" ")

			return SCHEDULE_ITEMS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get schedule items failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a schedule preview.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule preview is to be gotten from.
	Returns:
	dict: Returns the information of the gotten schedule preview.
	Exception: An error is thrown if the schedule preview fails to get.
	Exception: An error is thrown if the API type is not admin.
	"""
	def get_schedule_preview(self, SCHEDULE_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Getting schedule preview", sep=" ")

			SCHEDULE_PREVIEW_INFO = _get_schedule_preview(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Schedule preview gotten", sep=" ")

			return SCHEDULE_PREVIEW_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get schedule preview failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Moves a schedule item.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item is to be moved from.
	ITEM_ID (str): The id of the item to be moved.
	PREVIOUS_ITEM (str | None): The previous item of the schedule item.
	Returns:
	dict: Returns the information of the moved schedule item.
	Exception: An error is thrown if the schedule item fails to move.
	Exception: An error is thrown if the API type is not admin.
	"""
	def move_schedule_item(self, SCHEDULE_ID: str, ITEM_ID: str, PREVIOUS_ITEM: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Moving schedule item", sep=" ")

			SCHEDULE_ITEM_INFO = _move_schedule_item(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, PREVIOUS_ITEM, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item moved", sep=" ")

			return SCHEDULE_ITEM_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Move schedule item failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Publishes an intelligent schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule to be published.
	NUMBER_OF_LOCKED_DAYS (int): The number of locked days of the intelligent schedule.
	Returns:
	dict: Returns the information of the published schedule.
	Exception: An error is thrown if the schedule fails to publish.
	Exception: An error is thrown if the API type is not admin.
	"""
	def publish_intelligent_schedule(self, SCHEDULE_ID: str, NUMBER_OF_LOCKED_DAYS: int) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Publishing intelligent schedule", sep=" ")

			INTELLIGENT_SCHEDULE_INFO = _publish_intelligent_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, NUMBER_OF_LOCKED_DAYS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent schedule published", sep=" ")

			return INTELLIGENT_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Publish intelligent schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Starts a schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule to be started.
	SKIP_CLEANUP_ON_FAILURE (bool, None): Whether or not to skip cleanup on failure.
	Returns:
	dict: Returns the information of the started schedule.
	Exception: An error is thrown if the schedule fails to start.
	Exception: An error is thrown if the API type is not admin.
	"""
	def start_schedule(self, SCHEDULE_ID: str, SKIP_CLEANUP_ON_FAILURE: bool | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Starting schedule", sep=" ")

			SCHEDULE_INFO = _start_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, SKIP_CLEANUP_ON_FAILURE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule started", sep=" ")

			return SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Start schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Stops a schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule to be stopped.
	FORCE_STOP (bool, None): Whether or not to force a stop.
	Returns:
	dict: Returns the information of the stopped schedule.
	Exception: An error is thrown if the schedule fails to stop.
	Exception: An error is thrown if the API type is not admin.
	"""
	def stop_schedule(self, SCHEDULE_ID: str, FORCE_STOP: bool | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Stopping schedule", sep=" ")

			SCHEDULE_INFO = _stop_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, FORCE_STOP, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule stopped", sep=" ")

			return SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Stop schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates an intelligent playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the intelligent playlist is to be updated.
	COLLECTIONS (list[dict], None): The collections of the intelligent playlist. dict format: {"id": "string", "description": "string"}
	END_SEARCH_DATE (str, None): The end search date of the intelligent playlist. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	END_SEARCH_DURATION_IN_MINUTES (int, None): The end search duration in minutes of the intelligent playlist.
	NAME (str, None): The name of the intelligent playlist.
	RELATED_CONTENTS (list[dict], None): The related content of the intelligent playlist.
	SEARCH_DATE (str, None): The search date of the intelligent playlist. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	SEARCH_DURATION_IN_MINUTES (int, None): The search duration in minutes of the intelligent playlist.
	SEARCH_FILTER_TYPE (str, None): The search filter type of the intelligent playlist. Values: Random: 1, Random within a Date Range: 2, Newest: 3, Newest Not Played: 4
	TAGS (list[dict], None): The tags of the intelligent playlist.
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the intelligent playlist. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the updated intelligent playlist.
	Exception: An error is thrown if the intelligent playlist fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_intelligent_playlist(self, SCHEDULE_ID: str, COLLECTIONS: List[dict] | None,
									END_SEARCH_DATE: str | None, 
									END_SEARCH_DURATION_IN_MINUTES: int | None, NAME: str | None,
									RELATED_CONTENTS: List[dict] | None, SEARCH_DATE: str | None,
									SEARCH_DURATION_IN_MINUTES: int | None, SEARCH_FILTER_TYPE: int | None,
									TAGS: List[dict] | None, THUMBNAIL_ASSET: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating intelligent playlist", sep=" ")

			INTELLIGENT_PLAYLIST_INFO = _update_intelligent_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, COLLECTIONS, END_SEARCH_DATE, END_SEARCH_DURATION_IN_MINUTES, NAME, 
				RELATED_CONTENTS, SEARCH_DATE, SEARCH_DURATION_IN_MINUTES, SEARCH_FILTER_TYPE,
				TAGS, THUMBNAIL_ASSET, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Intelligent playlist updated", sep=" ")

			return INTELLIGENT_PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update intelligent playlist failed", sep=" ")
			raise Exception(error.args[0])	

	"""
	Description:
	Updates an intelligent schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the intelligent schedule is to be updated.
	DEFAULT_VIDEO_ASSET (dict): The default video asset of the intelligent schedule. dict format: {"id": "string", "description": "string"}
	NAME (str, None): The name of the intelligent schedule.
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the intelligent schedule. dict format: {"id": "string", "description": "string"}
	TIME_ZONE_ID (str, None): The time zone id of the intelligent schedule.
	Returns:
	dict: Returns the information of the updated intelligent schedule.
	Exception: An error is thrown if the intelligent schedule fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_intelligent_schedule(self, SCHEDULE_ID: str, DEFAULT_VIDEO_ASSET: dict,
									NAME: str | None, THUMBNAIL_ASSET: dict | None, 
									TIME_ZONE_ID: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating intelligent schedule", sep=" ")

			INTELLIGENT_SCHEDULE_INFO = _update_intelligent_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, DEFAULT_VIDEO_ASSET, NAME, THUMBNAIL_ASSET, TIME_ZONE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Intelligent schedule updated", sep=" ")

			return INTELLIGENT_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update intelligent schedule failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a playlist.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the playlist is to be updated from.
	DEFAULT_VIDEO_ASSET (list[dict], None): The default video asset of the playlist. dict format: {"id": "string", "description": "string"}
	LOOP_PLAYLIST (bool, None): Whether or not to loop the playlist.
	NAME (str, None): The name of the playlist.
	THUMBNAIL_ASSET (dict, None): The thumbnail asset of the playlist. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the updated playlist.
	Exception: An error is thrown if the playlist fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_playlist(self, SCHEDULE_ID: str, DEFAULT_VIDEO_ASSET: dict | None, LOOP_PLAYLIST: bool | None,
						NAME: str | None, THUMBNAIL_ASSET: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating playlist", sep=" ")

			PLAYLIST_INFO = _update_playlist(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, DEFAULT_VIDEO_ASSET, LOOP_PLAYLIST, NAME, THUMBNAIL_ASSET, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Playlist updated", sep=" ")

			return PLAYLIST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update playlist failed", sep=" ")
			raise Exception(error.args[0])	

	"""
	Description:
	Updates a playlist video.
	Parameters:
	PLAYLIST_ID (str): The id of the schedule the playlist video is to be updated from.
	ITEM_ID (str): The id of the item to be updated.
	ASSET (dict, None): The asset of the playlist video. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the updated playlist video.
	Exception: An error is thrown if the playlist video fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_playlist_video(self, PLAYLIST_ID: str, ITEM_ID: str, ASSET: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating playlist video", sep=" ")

			PLAYLIST_VIDEO_INFO = _update_playlist_video(self.token, self.config["serviceApiUrl"], 
				PLAYLIST_ID, ITEM_ID, ASSET, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Playlist video updated", sep=" ")

			return PLAYLIST_VIDEO_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update playlist video failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates a schedule item asset.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item asset is to be updated from.
	ITEM_ID (str): The id of the item to be updated.
	ASSET (dict, None): The asset of the schedule item asset. dict format: {"id": "string", "description": "string"}
	DAYS (list[dict], None): The days of the schedule item asset. dict format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str, None): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str, None): The end time code of the schedule item asset. Please use the following format: hh:mm:ss;ff.
	TIME_CODE (str, None): The time code of the schedule item asset. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the updated schedule item asset.
	Exception: An error is thrown if the schedule item asset fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_schedule_item_asset(self, SCHEDULE_ID: str, ITEM_ID: str, ASSET: dict | None,
								   DAYS: List[dict] | None, DURATION_TIME_CODE: str | None,
								   END_TIME_CODE: str | None, TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating schedule item asset", sep=" ")

			SCHEDULE_ITEM_ASSET_INFO = _update_schedule_item_asset(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, ASSET, DAYS, DURATION_TIME_CODE, END_TIME_CODE, TIME_CODE, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item asset updated", sep=" ")

			return SCHEDULE_ITEM_ASSET_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update schedule item asset failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a schedule item live channel.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item live channel is to be updated from.
	ITEM_ID (str): The id of the item to be updated.
	DAYS (list[dict], None): The days of the schedule item live channel. dict format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str, None): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str, None): The end time code of the schedule item live channel. Please use the following format: hh:mm:ss;ff.
	LIVE_CHANNEL (dict, None): The live channel of the schedule item live channel. dict format: {"id": "string", "description": "string"}
	TIME_CODE (str, None): The time code of the schedule item live channel. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the updated schedule item live channel.
	Exception: An error is thrown if the schedule item live channel fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_schedule_item_live_channel(self, SCHEDULE_ID: str, ITEM_ID: str, DAYS: List[dict] | None,
										  DURATION_TIME_CODE: str | None, END_TIME_CODE: str | None,
										  LIVE_CHANNEL: dict | None, TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating schedule item live channel", sep=" ")

			SCHEDULE_ITEM_LIVE_CHANNEL_INFO = _update_schedule_item_live_channel(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, DAYS, DURATION_TIME_CODE, END_TIME_CODE, LIVE_CHANNEL, TIME_CODE, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item live channel updated", sep=" ")

			return SCHEDULE_ITEM_LIVE_CHANNEL_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update schedule item live channel failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a schedule item playlist schedule.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item playlist schedule is to be updated from.
	ITEM_ID (str): The id of the item to be updated.
	DAYS (list[dict], None): The days of the schedule item playlist schedule. dict format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str, None): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str, None): The end time code of the schedule item playlist schedule. Please use the following format: hh:mm:ss;ff.
	PLAYLIST_SCHEDULE (dict, None): The playlist schedule of the schedule item playlist schedule. dict format: {"id": "string", "description": "string"}
	TIME_CODE (str, None): The time code of the schedule item playlist schedule. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the updated schedule item playlist schedule.
	Exception: An error is thrown if the schedule item playlist schedule fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_schedule_item_playlist_schedule(self, SCHEDULE_ID: str, ITEM_ID: str, DAYS: List[dict] | None,
											   DURATION_TIME_CODE: str | None, END_TIME_CODE: str | None,
											   PLAYLIST_SCHEDULE: dict | None, TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating schedule item playlist schedule", sep=" ")

			SCHEDULE_ITEM_PLAYLIST_SCHEDULE_INFO = _update_schedule_item_playlist_schedule(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, DAYS, DURATION_TIME_CODE, END_TIME_CODE, PLAYLIST_SCHEDULE, TIME_CODE, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item playlist schedule updated", sep=" ")

			return SCHEDULE_ITEM_PLAYLIST_SCHEDULE_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update schedule item playlist schedule failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates a schedule item search filter.
	Parameters:
	SCHEDULE_ID (str): The id of the schedule the schedule item search filter is to be updated from.
	ITEM_ID (str): The id of the item to be updated.
	COLLECTIONS (list[dict], None): The collections of the schedule item search filter. dict format: {"id": "string", "description": "string"}
	DAYS (list[dict], None): The days of the schedule item search filter. dict format: {"id": "string", "description": "string"}
	DURATION_TIME_CODE (str, None): The duration time between TIME_CODE and END_TIME_CODE. Please use the following format: hh:mm:ss;ff.
	END_SEARCH_DATE (str, None): The end search date of the schedule item search filter. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	END_SEARCH_DURATION_IN_MINUTES (int, None): The end search duration in minutes of the schedule item search filter.
	END_TIME_CODE (str, None): The end time code of the schedule item search filter. Please use the following format: hh:mm:ss;ff.
	RELATED_CONTENTS (list[dict], None): The related content of the schedule item search filter. dict format: {"id": "string", "description": "string"}
	SEARCH_DATE (str, None): The search date of the schedule item search filter. Only use when SEARCH_FILTER_TYPE = 2. Please use the following format: yyyy-MM-dd.THH:MM:SS.FFFZ.
	SEARCH_DURATION_IN_MINUTES (int, None): The search duration in minutes of the schedule item search filter.
	SEARCH_FILTER_TYPE (str, None): The search filter type of the schedule item search filter. Values: Random: 1, Random within a Date Range: 2, Newest: 3, Newest Not Played: 4
	TAGS (list[dict], None): The tags of the schedule item search filter. dict format: {"id": "string", "description": "string"}
	TIME_CODE (str, None): The time code of the schedule item search filter. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the updated schedule item search filter.
	Exception: An error is thrown if the schedule item search filter fails to update.
	Exception: An error is thrown if the API type is not admin.
	"""
	def update_schedule_item_search_filter(self, SCHEDULE_ID: str, ITEM_ID: str, COLLECTIONS: List[dict] | None,
										   DAYS: List[dict] | None, DURATION_TIME_CODE: str | None,
										   END_SEARCH_DATE: str | None, 
										   END_SEARCH_DURATION_IN_MINUTES: int | None,
										   END_TIME_CODE: str | None, RELATED_CONTENTS: List[dict] | None, 
										   SEARCH_DATE: str | None, SEARCH_DURATION_IN_MINUTES: int | None,
										   SEARCH_FILTER_TYPE: int | None, TAGS: List[dict] | None,
										   TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating schedule item search filter", sep=" ")

			SCHEDULE_ITEM_SEARCH_FILTER_INFO = _update_schedule_item_search_filter(self.token, self.config["serviceApiUrl"], 
				SCHEDULE_ID, ITEM_ID, COLLECTIONS, DAYS, DURATION_TIME_CODE, END_SEARCH_DATE, 
				END_SEARCH_DURATION_IN_MINUTES, END_TIME_CODE, RELATED_CONTENTS, SEARCH_DATE, 
				SEARCH_DURATION_IN_MINUTES, SEARCH_FILTER_TYPE, TAGS, TIME_CODE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Schedule item search filter updated", sep=" ")

			return SCHEDULE_ITEM_SEARCH_FILTER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update schedule item search filter failed", sep=" ")
			raise Exception(error.args[0])
		
	# User
	"""
	Description:
	Deletes a user.
	Parameters:
	USER_ID (str): The user ID of the user to be deleted.
	Returns:
	None: A promise that resolves when the user is deleted.
	Exception: An error is thrown if the user fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user(self, USER_ID: str) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User", sep=" ")
			_delete_user(self.token, self.config["serviceApiUrl"], USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Failed to Delete", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a user content attribute data.
	Parameters:
	USER_ID (str, None): The user ID of the user's content attribute data'. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user content attribute data is deleted.
	Exception: An error is thrown if the user content attribute data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_content_attribute_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Content Attribute Data", sep=" ")
			_delete_user_content_attribute_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Content Attribute Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Content Attribute Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user content group data.
	Parameters:
	USER_ID (str, None): The user ID of the user's content group data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user content group data is deleted.
	Exception: An error is thrown if the user content group data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_content_group_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Content Group Data", sep=" ")
			_delete_user_content_group_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Content Group Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Content Group Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user content security data.
	Parameters:
	CONTENT_ID (str, None): The content ID of the user content security data.
	CONTENT_DEFINITION_ID (str, None): The content definition ID of the user content security data.
	USER_ID (str, None): The user ID of the user's content security data. If set to None, the user ID of the current user is used.
	EMAIL (str, None): The email of the user content security data.
	ID (str, None): The ID of the user content security data.
	KEY_NAME (str, None): The key name of the user content security data.
	EXPIRATION_DATE (str, None): The expiration date of the user content security data.
	Returns:
	None: A promise that resolves when the user content security data is deleted.
	Exception: An error is thrown if the user content security data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_content_security_data(self, CONTENT_ID: str | None, CONTENT_DEFINITION_ID: str | None,
										  USER_ID: str | None, EMAIL: str | None, ID: str | None,
										  KEY_NAME: str | None, EXPIRATION_DATE: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Content Security Data", sep=" ")
			_delete_user_content_security_data(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, CONTENT_DEFINITION_ID, USER_ID, EMAIL, ID, KEY_NAME, EXPIRATION_DATE, 
				self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Content Security Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Content Security Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a user's data.
	Parameters:
	USER_ID (str, None): The user ID of the user's data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user data is deleted.
	Exception: An error is thrown if the user data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.id
			
			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Data", sep=" ")
			_delete_user_data(self.token, self.config["serviceApiUrl"], USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user dislikes data.
	Parameters:
	USER_ID (str, None): The user ID of the user's dislike data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user dislikes data is deleted.
	Exception: An error is thrown if the user dislikes data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_dislikes_data(self, USER_ID: str | None) -> None:
		try:
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Dislikes Data", sep=" ")
			_delete_user_dislike_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Dislikes Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Dislikes Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a user favorites data.
	Parameters:
	USER_ID (str, None): The user ID of the user's favorites data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user favorites data is deleted.
	Exception: An error is thrown if the user favorites data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_favorites_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			if USER_ID is None:
				USER_ID = self.id
			
			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Favorites Data", sep=" ")
			_delete_user_favorites_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Favorites Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Favorites Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user likes data.
	Parameters:
	USER_ID (str, None): The user ID of the user's likes data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user likes data is deleted.
	Exception: An error is thrown if the user likes data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_likes_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Likes Data", sep=" ")
			_delete_user_likes_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Likes Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Likes Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user saved search data.
	Parameters:
	USER_ID (str, None): The user ID of the user's saved search data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user saved search data is deleted.
	Exception: An error is thrown if the user saved search data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_saved_search_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Saved Search Data", sep=" ")
			_delete_user_saved_search_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Saved Search Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Saved Search Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user session data.
	Parameters:
	USER_ID (str, None): The user ID of the user's session data. If set to None, the user ID of the current user is used.
	Returns:
	None: A promise that resolves when the user session data is deleted.
	Exception: An error is thrown if the user session data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_session_data(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Session Data", sep=" ")
			_delete_user_session_data(self.token, self.config["serviceApiUrl"], 
				USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Session Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Session Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Deletes a user video tracking data.
	Parameters:
	ASSET_ID (str, None): The asset ID of the user video tracking data.
	CONTENT_ID (str, None): The content ID of the user video tracking data.
	VIDEO_TRACKING_ATTRIBUTE_ID (str, None): The video tracking attribute ID of the user video tracking data. Possible values: "Undefined", "Watchlist", "LiveStream".
	USER_ID (str, None): The user ID of the user video tracking data. If set to None, the user ID of the current user is used.
	ID (str, None): The ID of the user video tracking data.
	IS_FIRST_QUARTILE (bool, None): The first quartile of the user video tracking data.
	IS_MIDPOINT (bool, None): The midpoint of the user video tracking data.
	IS_THIRD_QUARTILE (bool, None): The third quartile of the user video tracking data.
	IS_COMPLETE (bool, None): The complete of the user video tracking data.
	IS_HIDDEN (bool, None): The hidden of the user video tracking data.
	IS_LIVE_STREAM (bool, None): The live stream of the user video tracking data.
	MAX_SECOND (float, None): The max second of the user video tracking data.
	LAST_SECOND (float, None): The last second of the user video tracking data.
	TOTAL_SECONDS (float, None): The total seconds of the user video tracking data.
	LAST_BEACON_DATE (str, None): The last beacon date of the user video tracking data.
	KEY_NAME (str, None): The key name of the user video tracking data.
	Returns:
	None: A promise that resolves when the user video tracking data is deleted.
	Exception: An error is thrown if the user video tracking data fails to delete.
	Exception: An error is thrown if the API type is not admin.
	"""
	def delete_user_video_tracking_data(self, ASSET_ID: str | None, CONTENT_ID: str | None,
										VIDEO_TRACKING_ATTRIBUTE_ID: str | None, USER_ID: str | None,
										ID: str | None, IS_FIRST_QUARTILE: bool | None, IS_MIDPOINT: bool | None,
										IS_THIRD_QUARTILE: bool | None, IS_COMPLETE: bool | None, IS_HIDDEN: bool | None,
										IS_LIVE_STREAM: bool | None, MAX_SECOND: float | None, LAST_SECOND: float | None,
										TOTAL_SECONDS: float | None, LAST_BEACON_DATE: str | None, KEY_NAME: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Deleting User Video Tracking Data", sep=" ")
			_delete_user_video_tracking_data(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, CONTENT_ID, VIDEO_TRACKING_ATTRIBUTE_ID, USER_ID, ID, IS_FIRST_QUARTILE, 
				IS_MIDPOINT, IS_THIRD_QUARTILE, IS_COMPLETE, IS_HIDDEN, IS_LIVE_STREAM, MAX_SECOND, 
				LAST_SECOND, TOTAL_SECONDS, LAST_BEACON_DATE, KEY_NAME, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Video Tracking Data Deleted", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User Video Tracking Data Failed to Delete", sep=" ")
			raise Exception(error.args[0])

	# User Session
	"""
	Description:
	Changes the status of a user session.
	Parameters:
	ID (str, None): The ID of the user session. If set to None, the user ID of the current user is used.
	USER_SESSION_STATUS (str): The status of the user session.
	APPLICATION_ID (str, None): The application ID of the user session.
	Returns:
	None: A promise that resolves when the status of the user session is changed.
	Exception: An error is thrown if the status of the user session fails to change.
	Exception: An error is thrown if the API type is not admin.
	"""
	def change_session_status(self, USER_ID: str | None, USER_SESSION_STATUS: str, APPLICATION_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			if USER_ID is None:
				USER_ID = self.user_session_id

			print(datetime.now().strftime('%H:%M:%S'), "Changing Session Status", sep=" ")
			_change_session_status(self.token, self.config["serviceApiUrl"], 
				USER_ID, USER_SESSION_STATUS, APPLICATION_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "Session Status Changed", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets a user session.
	Parameters:
	ID (str, None): The ID of the user session. If set to None, the user ID of the current user is used.
	Returns:
	dict: Returns the information of the gotten user session.
	Exception: An error is thrown if the user session fails to get.
	"""
	def get_user_session(self, USER_ID: str | None) -> dict:
		try:
			if USER_ID is None:
				USER_ID = self.id

			print(datetime.now().strftime('%H:%M:%S'), "Getting User Session", sep=" ")
			USER_SESSION_INFO = _get_user_session(self.token, self.config["serviceApiUrl"], 
				self.config["apiType"], USER_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "User Session Got", sep=" ")

			return USER_SESSION_INFO
		except Exception as error:
			raise Exception(error.args[0])

	# Common
	"""
	Description:
	Sends password to the user's email containing code used to reset password.
	Parameters:
	Returns:
	None
	Exception: If forgot password fails.
	"""
	def forgot_password(self) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start forgot password", sep=" ")

			_forgot_password(self.config["serviceApiUrl"], self.config["username"], 
					self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Forgot password complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Forgot password failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Resets the user's password.
	Parameters:
	CODE (str): The code of the user.
	NEW_PASSWORD (str): The new password of the user.
	Returns:
	None
	Exception: If reset password fails.
	"""
	def reset_password(self, CODE: str, NEW_PASSWORD: str) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start reset password", sep=" ")

			_reset_password(self.config["serviceApiUrl"], self.config["username"], CODE, NEW_PASSWORD, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Reset password complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Reset password failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Logs the user out.
	Parameters:
	None
	Exception: If logout fails.
	"""
	def logout(self) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start logout", sep=" ")

			_logout(self.token, self.config["serviceApiUrl"], self.user_session_id, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Logout complete", sep=" ")

			self.token = None
			self.refresh_token = None
			self.expiration_seconds = None
			self.user_session_id = None
			self.id = None

		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Logout failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Sends a code to the user's email to verify the account.
	Parameters:
	EMAIL (str): The email of the user.
	FIRST_NAME (str | None): The first name of the user.
	LAST_NAME (str | None): The last name of the user.
	PASSWORD (str): The password of the user.
	Returns:
	None
	Exception: If register fails.
	"""
	def register(self, EMAIL: str, FIRST_NAME: str | None, LAST_NAME: str | None, PASSWORD: str) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start register", sep=" ")

			_register(self.config["serviceApiUrl"], EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Register complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Register failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Resends the verification email.
	Paremeters:
	EMAIL (str): The email of the user.
	Returns:
	None
	Exception: If resend verification email fails.
	"""
	def resend_code(self, EMAIL: str) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start resend code", sep=" ")

			_resend_code(self.config["serviceApiUrl"], EMAIL, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Resend code complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Resend code failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Verifies the user's account.
	Parameters:
	EMAIL (str): The email of the user.
	CODE (str): The code of the user.
	Returns:
	None
	Exception: If verify fails.
	"""
	def verify(self, EMAIL: str, CODE: str) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start verify", sep=" ")

			VERIFICATION_INFO = _verify(self.config["serviceApiUrl"], EMAIL, 
							   CODE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Verify complete", sep=" ")

			return VERIFICATION_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Verify failed", sep=" ")
			raise Exception(error.args[0])

	# Asset
	"""
	Description:
	Archives an asset.
	Parameters:
	ASSET_ID (str): The id of the asset.
	Returns:
	dict: A promise that resolves when the asset is archived.
	Returns the information of the archived asset.
	Exception:
	If the asset fails to archive.
	If the API type is not admin.
	"""
	def archive_asset(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Archiving asset", sep=" ")

			ARCHIVED_ASSET_INFO = _archive_asset(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset archived", sep=" ")

			return ARCHIVED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Builds a media.
	Parameters:
	SOURCES (list of dict): The sources of the media. dict format: {"sourceAssetId": "string", "startTimeCode": "string", "endTimeCode": "string"}
	TITLE (str |None): The title of the media.
	TAGS (list of dict | None): The tags of the media. dict format: {"id": "string", "description": "string"}
	COLLECTIONS (list of dict | None): The collections of the media. dict format: {"id": "string", "description": "string"}
	RELATED_CONTENTS (list of dict | None): The related contents of the media. dict format: {"id": "string", "description": "string"}
	DESTINATION_FOLDER_ID (str): The destination folder ID of the media.
	VIDEO_BITRATE (int | None): The video bitrate of the media.
	AUDIO_TRACKS (list of dict | None): The audio tracks of the media. 
	dict format: { "id": "string", "bitRate": "int", "sampleRate": "int", "numChannels": "int", "format": "string", "frameRate": "int", "bitDepth": "int", "bitRateMode": "string", "durationSeconds": "int"}
	Returns:
	None
	Exception:
	If the media fails to build.
	If the API type is not portal.
	"""
	def build_media(self, SOURCES: List[dict], TITLE: str | None, TAGS: List[dict] | None, 
				    COLLECTIONS: List[dict] | None, RELATED_CONTENTS: List[dict] | None, 
				 	DESTINATION_FOLDER_ID: str, VIDEO_BITRATE: int | None, 
					AUDIO_TRACKS: List[dict] | None) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Building media", sep=" ")

			_build_media(self.token, self.config["serviceApiUrl"], SOURCES, TITLE, TAGS, COLLECTIONS, 
				RELATED_CONTENTS, DESTINATION_FOLDER_ID, VIDEO_BITRATE, AUDIO_TRACKS, self.debug_mode)
		
			print(datetime.now().strftime('%H:%M:%S'), "Media built", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])		

	"""
	Description:
	Clips an asset.
	Parameters:
	ASSET_ID (str): The id of the asset.
	START_TIME_CODE (str): The start time code of the asset. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str): The end time code of the asset. Please use the following format: hh:mm:ss;ff.
	TITLE (str): The title of the asset.
	OUTPUT_FOLDER_ID (str): The output folder ID of the asset.
	TAGS (list of dict | None): The tags of the asset. dict format: {"id": "string", "description": "string"}
	COLLECTIONS (list of dict | None): The collections of the asset. dict format: {"id": "string", "description": "string"}
	RELATED_CONTENTS (list of dict | None): The related contents of the asset. dict format: {"id": "string", "description": "string"}
	VIDEO_BITRATE (int | None): The video bitrate of the asset.
	AUDIO_TRACKS (list of dict | None): The audio tracks of the asset. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the clipped asset.
	Exception:
	If the asset fails to clip.
	"""
	def clip_asset(self, ASSET_ID: str, START_TIME_CODE: str, END_TIME_CODE: str, TITLE: str, 
				   OUTPUT_FOLDER_ID: str, TAGS: List[dict] | None, COLLECTIONS: List[dict] | None, 
				   RELATED_CONTENTS: List[dict] | None, VIDEO_BITRATE: int | None, 
				   AUDIO_TRACKS: List[dict] | None) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Clipping asset", sep=" ")

			CLIPPED_ASSET_INFO = _clip_asset(self.token, self.config["serviceApiUrl"],
				ASSET_ID, self.config["apiType"], START_TIME_CODE, END_TIME_CODE, 
				TITLE, OUTPUT_FOLDER_ID, TAGS, COLLECTIONS, RELATED_CONTENTS, 
				VIDEO_BITRATE, AUDIO_TRACKS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset clipped", sep=" ")

			return CLIPPED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Copys an asset.
	Parameters:
	ASSET_IDS (list): The ids of the asset.
	DESTINATION_FOLDER_ID (str): The destination folder ID of the asset.
	BATCH_ACTION (dict | None): The actions to be performed. dict format: {"id": "string", "description": "string"}
	CONTENT_DEFINITION_ID (str |None): The content definition ID of the asset.
	SCHEMA_NAME (str |None): The schema name of the asset. Note that we convert all incoming keys to lower first char to help with serialization for dict later. dict format: {"key": "string", "value": "string"}
	RESOLVER_EXCEMPT (boolean | None): The resolver excempt of the asset.
	Returns:
	dict: Returns the information of the performed assets.
	Exception:
	If the assets fail to perform.
	If the API type is not admin.
	"""
	def copy_asset(self, ASSET_IDS: List[str], DESTINATION_FOLDER_ID: str, 
				   BATCH_ACTION: dict | None, CONTENT_DEFINITION_ID: str | None, 
				   SCHEMA_NAME: str | None, RESOLVER_EXCEMPT: bool | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Copying asset", sep=" ")

			COPIED_ASSET_INFO = _copy_asset(self.token, self.config["serviceApiUrl"], 
				ASSET_IDS, DESTINATION_FOLDER_ID, BATCH_ACTION, CONTENT_DEFINITION_ID, 
				SCHEMA_NAME, RESOLVER_EXCEMPT, self.id, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset copied", sep=" ")

			return COPIED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates an annotation.
	Parameters:
	ASSET_ID (str): The id of the asset.
	START_TIME_CODE (str): The start time code of the annotation. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str |None): The end time code of the annotation. Please use the following format: hh:mm:ss;ff.
	FIRST_KEYWORD (str): The first keyword of the annotation.
	SECOND_KEYWORD (str): The second keyword of the annotation.
	DESCRIPTION (str): The description of the annotation.
	COUNTRY (dict): The country of the annotation. dict format: {"id": "string", "description": "string"}
	CONTENT_ID (str |None): The content ID of the annotation.
	IMAGE_URL (str |None): The image URL of the annotation.
	Returns:
	dict: Returns the information of the created annotation.
	Exception:
	If the annotation fails to create.
	If the API type is not portal.
	"""
	def create_annotation(self, ASSET_ID: str, START_TIME_CODE: str, END_TIME_CODE: str, 
					      FIRST_KEYWORD: str, SECOND_KEYWORD: str, DESCRIPTION: str, 
						  COUNTRY: dict, CONTENT_ID: str | None, IMAGE_URL: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating annotation", sep=" ")

			ANNOTATION_INFO = _create_annotation(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, START_TIME_CODE, END_TIME_CODE, FIRST_KEYWORD, SECOND_KEYWORD, DESCRIPTION, 
				COUNTRY, CONTENT_ID, IMAGE_URL, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Annotation created", sep=" ")

			return ANNOTATION_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates an asset ad break.
	Parameters:
	ASSET_ID (str): The id of the asset.
	TIME_CODE (str |None): The time code of the asset ad break. Please use the following format: hh:mm:ss;ff.
	TAGS (list of dict | None): The tags of the asset ad break. dict format: {"id": "string", "description": "string"}
	LABELS (list of dict | None): The labels of the asset ad break. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the created asset ad break.
	Exception:
	If the asset ad break fails to create.
	If the API type is not admin.
	"""
	def create_asset_ad_break(self, ASSET_ID: str, TIME_CODE: str | None,
						      TAGS: List[dict] | None, LABELS: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating asset ad break", sep=" ")

			ASSET_AD_BREAK_INFO = _create_asset_ad_break(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, TIME_CODE, TAGS, LABELS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset ad break created", sep=" ")

			return ASSET_AD_BREAK_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates a folder asset.
	Parameters:
	PARENT_ID (str): The parent asset id for the parent folder.
	DISPLAY_NAME (str): The visual name of the new folder. It can contain spaces and other characters.
	Returns:
	dict: Returns the information of the created folder asset.
	Exception:
	If the folder asset fails to create.
	If the API type is not admin.
	"""
	def create_folder_asset(self, PARENT_ID: str, DISPLAY_NAME: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating folder asset", sep=" ")

			FOLDER_ASSET_INFO = _create_folder_asset(self.token, self.config["serviceApiUrl"], 
				PARENT_ID, DISPLAY_NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Folder asset created", sep=" ")

			return FOLDER_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates a placeholder asset.
	Parameters:
	PARENT_ID (str): The parent asset id for the placeholder asset.
	ASSET_NAME (str): The visual name of the new placeholder. It can contain spaces and other characters, must contain file extension.
	Returns:
	dict: Returns the information of the created placeholder asset.
	Exception:
	If the placeholder asset fails to create.
	If the API type is not admin.
	"""
	def create_placeholder_asset(self, PARENT_ID: str, ASSET_NAME: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating placeholder asset", sep=" ")

			PLACEHOLDER_ASSET_INFO = _create_placeholder_asset(self.token, self.config["serviceApiUrl"], 
				PARENT_ID, ASSET_NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Placeholder asset created", sep=" ")

			return PLACEHOLDER_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates a screenshot at a timecode.
	Parameters:
	ASSET_ID (str): The id of the asset.
	TIME_CODE (str |None): The time code of the screenshot. Please use the following format: hh:mm:ss;ff.
	Returns:
	dict: Returns the information of the created screenshot.
	Exception:
	If the screenshot fails to create.
	If the API type is not admin.
	"""
	def create_screenshot_at_timecode(self, ASSET_ID: str, TIME_CODE: str | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Creating screenshot at timecode", sep=" ")

			SCREENSHOT_INFO = _create_screenshot_at_timecode(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, TIME_CODE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Screenshot created at timecode", sep=" ")

			return SCREENSHOT_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Deletes an annotation.
	Parameters:
	ASSET_ID (str): The id of the asset of the annotation.
	ANNOTATION_ID (str): The id of the annotation.
	Returns:
	dict: Returns the information of the deleted annotation.
	Exception:
	If the annotation fails to delete.
	If the API type is not portal.
	"""
	def delete_annotation(self, ASSET_ID: str, ANNOTATION_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Deleting annotation", sep=" ")

			DELETED_ANNOTATION_INFO = _delete_annotation(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, ANNOTATION_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Annotation deleted", sep=" ")

			return DELETED_ANNOTATION_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Deletes an asset.
	Parameters:
	ASSET_ID (str): The id of the asset.
	Returns:
	dict: Returns the information of the deleted asset.
	Exception:
	If the asset fails to delete.
	If the API type is not admin.
	"""
	def delete_asset(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Deleting asset", sep=" ")

			DELETED_ASSET_INFO = _delete_asset(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset deleted", sep=" ")

			return DELETED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Deletes an asset ad break.
	Parameters:
	ASSET_ID (str): The id of the asset.
	AD_BREAK_ID (str): The id of the ad break.
	Returns:
	dict: Returns the information of the deleted asset ad break.
	Exception:
	If the asset ad break fails to delete.
	If the API type is not admin.
	"""
	def delete_asset_ad_break(self, ASSET_ID: str, AD_BREAK_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Deleting asset ad break", sep=" ")
			
			DELETED_ASSET_AD_BREAK_INFO = _delete_asset_ad_break(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, AD_BREAK_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset ad break deleted", sep=" ")

			return DELETED_ASSET_AD_BREAK_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Downloads an archive asset.
	Parameters:
	ASSET_IDS (list of str): The ids of the assets.
	FILE_NAME (str |None): The file name of the archive asset. Only use if apiType is admin.
	DOWNLOAD_PROXY (boolean | None): The download proxy of the archive asset. Only use if apiType is admin.
	Returns:
	dict: Returns the information of the downloaded archive asset.
	Exception:
	If the archive asset fails to download.
	"""
	def download_archive_asset(self, ASSET_IDS: List[str], FILE_NAME: str | None,
							   DOWNLOAD_PROXY: bool | None) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Downloading archive asset", sep=" ")

			DOWNLOADED_ARCHIVE_ASSET_INFO = _download_archive_asset(self.token, 
			    self.config["serviceApiUrl"], self.config["apiType"],
				ASSET_IDS, FILE_NAME, DOWNLOAD_PROXY, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Archive asset downloaded", sep=" ")

			return DOWNLOADED_ARCHIVE_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Duplicates an asset.
	Parameters:
	ASSET_ID (str): The id of the asset.
	Returns:
	dict: Returns the information of the duplicated asset.
	Exception:
	If the asset fails to duplicate.
	If the API type is not admin.
	"""
	def duplicate_asset(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Duplicating asset", sep=" ")

			DUPLICATED_ASSET_INFO = _duplicate_asset(self.token, self.config["serviceApiUrl"],
				ASSET_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset duplicated", sep=" ")

			return DUPLICATED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the annotations for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the annotations for.
	Returns:
	dict: Returns the annotations.
	Exception:
	If the annotations fail to retrieve.
	If the API type is not portal.
	"""
	def get_annotations(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting annotations", sep=" ")
			
			ANNOTATIONS = _get_annotations(self.token, self.config["serviceApiUrl"], ASSET_ID, 
				self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Annotations got", sep=" ")

			return ANNOTATIONS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the asset for.
	Returns:
	dict: Returns the asset.
	Exception:
	If the asset fails to retrieve.
	If the API type is not admin.
	"""
	def get_asset(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset", sep=" ")
			
			ASSET = _get_asset(self.token, self.config["serviceApiUrl"], ASSET_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset got", sep=" ")

			return ASSET
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the asset ad breaks for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the asset ad breaks for.
	Returns:
	dict: Returns the asset ad breaks.
	Exception:
	If the asset ad breaks fail to retrieve.
	If the API type is not admin.
	"""
	def get_asset_ad_breaks(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Getting asset ad breaks", sep=" ")
			
			ASSET_AD_BREAKS = _get_asset_ad_breaks(self.token, self.config["serviceApiUrl"], ASSET_ID, 
				self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset ad breaks got", sep=" ")

			return ASSET_AD_BREAKS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset child nodes for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the asset child nodes for.
	FOLDER_ID (str): The ID of the folder the asset is in.
	SORT_COLUMN (str): The column to sort by.
	IS_DESC (bool): Whether the sort is descending or not.
	PAGE_INDEX (int): The page index of the asset child nodes.
	PAGE_SIZE (int): The page size of the asset child nodes.
	Returns:
	dict: Returns the asset child nodes.
	Exception:
	If the asset child nodes fail to retrieve.
	If the API type is not admin.
	"""
	def get_asset_child_nodes(self, ASSET_ID: str, FOLDER_ID: str, SORT_COLUMN: str, 
						      IS_DESC: bool, PAGE_INDEX: int, PAGE_SIZE: int) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset child nodes", sep=" ")
			
			ASSET_CHILD_NODES = _get_asset_child_nodes(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, FOLDER_ID, SORT_COLUMN, IS_DESC, PAGE_INDEX, PAGE_SIZE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset child nodes got", sep=" ")

			return ASSET_CHILD_NODES
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset details for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the details for.
	Returns:
	dict: Returns the asset details.
	Exception:
	If the asset details fail to retrieve.
	"""
	def get_asset_details(self, ASSET_ID: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Getting asset details", sep=" ")

			ASSET_DETAILS = _get_asset_details(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, self.config["apiType"], self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset details got", sep=" ")

			return ASSET_DETAILS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset manifest with cookies for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the manifest with cookies for.
	COOKIE_ID (str): The ID of the cookie.
	Returns:
	dict: Returns the asset manifest with cookies.
	Exception:
	If the asset manifest with cookies fail to retrieve.
	"""
	def get_asset_manifest_with_cookies(self, ASSET_ID: str, COOKIE_ID: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Getting asset manifest with cookies", sep=" ")

			ASSET_MANIFEST_WITH_COOKIES = _get_asset_manifest_with_cookies(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, COOKIE_ID, self.config["apiType"],
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset manifest with cookies got", sep=" ")

			return ASSET_MANIFEST_WITH_COOKIES
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the asset metadata summary for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the metadata summary for.
	Returns:
	dict: Returns the asset metadata summary.
	Exception:
	If the asset metadata summary fails to retrieve.
	If the API type is not admin.
	"""
	def get_asset_metadata_summary(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset metadata summary", sep=" ")
			
			ASSET_METADATA_SUMMARY = _get_asset_metadata_summary(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset metadata summary got", sep=" ")

			return ASSET_METADATA_SUMMARY
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the list of all parent folders for this item. It does not include the item itself or any files in any folder. The folders will be returned in hierarchical sequence, starting from the top node and each identifiers object will have a new children attribute that is the next sub-folder in the hierarchy.
	Parameters:
	ASSET_ID (str): The assetId of the current item to get the parents for. This can be either a folder or a file.
	PAGE_SIZE (int): The size of the page of folders to retrieve. Note this is for each level of the tree.
	Returns:
	dict: Returns the asset parent folders.
	Exception:
	If the asset parent folders fail to retrieve.
	If the API type is not admin.
	"""
	def get_asset_parent_folders(self, ASSET_ID: str, PAGE_SIZE: int) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset parent folders", sep=" ")
			
			ASSET_PARENT_FOLDERS = _get_asset_parent_folders(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, PAGE_SIZE, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset parent folders got", sep=" ")

			return ASSET_PARENT_FOLDERS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset screenshot details for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the screenshot details for.
	SEGMENT_ID (str): The ID of the segment.
	SCREENSHOT_ID (str): The ID of the screenshot.
	Returns:
	dict: Returns the asset screenshot details.
	Exception:
	If the asset screenshot details fail to retrieve.
	If the API type is not admin.
	"""
	def get_asset_screenshot_details(self, ASSET_ID: str, SEGMENT_ID: str, 
								     SCREENSHOT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset screenshot details", sep=" ")
			
			ASSET_SCREENSHOT_DETAILS = _get_asset_screenshot_details(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, SEGMENT_ID, SCREENSHOT_ID, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset screenshot details got", sep=" ")

			return ASSET_SCREENSHOT_DETAILS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the asset segment details for the specified asset ID.
	Parameters:
	ASSET_ID (str): The ID of the asset to get the segment details for.
	SEGMENT_ID (str): The ID of the segment.
	Returns:
	dict: Returns the asset segment details.
	Exception:
	If the asset segment details fail to retrieve.
	If the API type is not admin.
	"""
	def get_asset_segment_details(self, ASSET_ID: str, SEGMENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting asset segment details", sep=" ")
			
			ASSET_SEGMENT_DETAILS = _get_asset_segment_details(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, SEGMENT_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset segment details got", sep=" ")

			return ASSET_SEGMENT_DETAILS
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets the user upload parts for the specified asset ID.
	Parameters:
	UPLOAD_ID (str): The ID of the upload to get the user upload parts for.
	Returns:
	dict: Returns the user upload parts.
	Exception:
	If the user upload parts fail to retrieve.
	If the API type is not admin.
	"""
	def get_user_upload_parts(self, UPLOAD_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting user upload parts", sep=" ")
			
			USER_UPLOAD_PARTS = _get_user_upload_parts(self.token, 
				self.config["serviceApiUrl"], UPLOAD_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "User upload parts got", sep=" ")

			return USER_UPLOAD_PARTS
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Gets the user uploads for the specified asset ID.
	Parameters:
	INCLUDE_COMPLETED_UPLOADS (boolean): Whether to include completed uploads or not.
	Returns:
	dict: Returns the upload uploads.
	Exception:
	If the user uploads fail to retrieve.
	If the API type is not admin.
	"""
	def get_user_uploads(self, INCLUDE_COMPLETED_UPLOADS: bool) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Getting user uploads", sep=" ")
			
			UPLOAD_UPLOADS = _get_user_uploads(self.token, 
				self.config["serviceApiUrl"], INCLUDE_COMPLETED_UPLOADS, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "User uploads got", sep=" ")

			return UPLOAD_UPLOADS
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Imports annotations.
	Parameters:
	ASSET_ID (str): The ID of the asset to import the annotations for.
	ANNOTATIONS (list of dict): The annotations to import. dict format: {"startTimeCode": "string", "endTimeCode": "string"}
	Returns:
	dict: Returns the information of the imported annotations.
	Exception:
	If the annotations fail to import.
	If the API type is not portal.
	"""
	def import_annotations(self, ASSET_ID: str, ANNOTATIONS: List[dict]) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Importing annotations", sep=" ")
			
			_import_annotations(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, ANNOTATIONS, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Annotations imported", sep=" ")
			
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Indexes an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to index.
	Returns:
	dict: Returns the information of the indexed asset.
	Exception:
	If the asset fails to index.
	If the API type is not admin.
	"""
	def index_asset(self, ASSET_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Indexing asset", sep=" ")
			
			INDEXED_ASSET_INFO = _index_asset(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset indexed", sep=" ")

			return INDEXED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Local restores an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to local restore.
	PROFILE (str |None): The profile of the local restore.
	Returns:
	dict: Returns the information of the local restored asset.
	Exception:
	If the asset fails to local restore.
	If the API type is not portal.
	"""
	def local_restore_asset(self, ASSET_ID: str, PROFILE: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Local restoring asset", sep=" ")
			
			LOCAL_RESTORED_ASSET_INFO = _local_restore_asset(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, PROFILE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset local restored", sep=" ")

			return LOCAL_RESTORED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Moves an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to move.
	DESTINATION_FOLDER_ID (str): The destination folder ID of the move.
	BATCH_ACTION (dict | None): The batch action of the move.
	CONTENT_DEFINITION_ID (str |None): The content definition ID of the move.
	SCHEMA_NAME (str |None): The schema name of the move.
	RESOLVER_EXCEMPT (boolean | None): The resolver exempt of the move.
	Returns:
	dict: Returns the information of the moved asset.
	Exception:
	If the asset fails to move.
	If the API type is not admin.
	"""
	def move_asset(self, ASSET_ID: str, DESTINATION_FOLDER_ID: str, BATCH_ACTION: dict | None,
				   CONTENT_DEFINITION_ID: str, SCHEMA_NAME: str | None, 
				   RESOLVER_EXCEMPT: bool | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Moving asset", sep=" ")

			MOVED_ASSET_INFO = _move_asset(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, DESTINATION_FOLDER_ID, 
				BATCH_ACTION, CONTENT_DEFINITION_ID, SCHEMA_NAME, self.id, RESOLVER_EXCEMPT, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset moved", sep=" ")

			return MOVED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Records an asset tracking beacon for the asset (either an ad or a normal asset).
	Parameters:
	ASSET_ID (str): The ID of the asset to record the asset tracking beacon for.
	TRACKING_EVENT (str): The tracking event of the asset tracking beacon. Enum: "Progress", "FirstQuartile", "Midpoint", "ThirdQuartile", "Complete", "Hide", "LiveStream"
	LIVE_CHANNEL_ID (str): The live channel ID of the asset tracking beacon.
	CONTENT_ID (str |None): Optional content Id to track along with required asset id.
	SECOND (int): Second mark into the video/ad.
	Returns:
	None
	Exception:
	If the asset tracking beacon fails to record.
	If the API type is not portal.
	"""
	def records_asset_tracking_beacon(self, ASSET_ID: str, TRACKING_EVENT: str, 
								     LIVE_CHANNEL_ID: str, CONTENT_ID: str | None, 
									 SECOND: int) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Recording asset tracking beacon", sep=" ")
			
			_records_asset_tracking_beacon(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, TRACKING_EVENT, LIVE_CHANNEL_ID, CONTENT_ID, SECOND, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset tracking beacon recorded", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Registers an asset.
	Parameters:
	ASSET_ID (str | null): The ID of the asset to register.
	PARENT_ID (str | null): The ID of the parent.
	DISPLAY_OBJECT_KEY (str |None): The display object key of the register.
	BUCKET_NAME (str): The bucket name of the register.
	OBJECT_KEY (str): The object key of the register.
	E_TAG (str |None): The eTag of the register.
	TAG_IDS (list of str | None): The tags of the register.
	COLLECTION_IDS (list of str | None): The collections of the register.
	RELATED_CONTENT_IDS (list of str | None): The related contents of the register.
	SEQUENCER (str |None): The sequencer of the register.
	ASSET_STATUS (str |None): The asset status of the register. Enum: "Available", "Renaming", "Copying", "Restoring", "Registering", "Uploading", "Archiving", "Archived", "PendingArchive", "PendingRestore", "Restored", "Deleting", "Moving", "SlugReplaced", "Updating", "Error", "Assembling", "Clipping", "Placeholder"
	STORAGE_CLASS (str |None): The storage class of the register. Enum: "Standard", "ReducedRedundancy", "Glacier", "StandardInfrequentAccess", "OneZoneInfrequentAccess", "IntelligentTiering", "DeepArchive", "GlacierInstanctRetrival", "Outposts"
	ASSET_TYPE (str |None): The asset type of the register. Enum: "Folder", "File", "Bucket"
	CONTENT_LENGTH (int | None): The content length of the register.
	STORAGE_EVENT_NAME (str |None): The storage event name of the register.
	CREATED_DATE (str |None): The created date of the register.
	STORAGE_SOURCE_IP_ADDRESS (str |None): The storage source IP address of the register.
	START_MEDIA_PROCESSOR (boolean | null): The start media processor of the register.
	DELETE_MISSING_ASSET (boolean | null): The delete missing asset of the register.
	Returns:
	dict: Returns the information of the registered asset.
	Exception:
	If the asset fails to register.
	If the API type is not admin.
	"""
	def register_asset(self, ASSET_ID: str | None, PARENT_ID: str | None, 
					   DISPLAY_OBJECT_KEY: str | None, BUCKET_NAME: str, OBJECT_KEY: str, 
					   E_TAG: str | None, TAG_IDS: List[str] | None, 
					   COLLECTION_IDS: List[str] | None, RELATED_CONTENT_IDS: List[str] | None,
					   SEQUENCER: str | None,ASSET_STATUS: str | None, 
					   STORAGE_CLASS: str | None, ASSET_TYPE: str | None, 
					   CONTENT_LENGTH: int | None, STORAGE_EVENT_NAME: str | None, 
					   CREATED_DATE: str | None, STORAGE_SOURCE_IP_ADDRESS: str | None,
					   START_MEDIA_PROCESSOR: bool | None, 
					   DELETE_MISSING_ASSET: bool | None) -> dict:
		
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Registering asset", sep=" ")
			
			REGISTERED_ASSET_INFO = _register_asset(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, PARENT_ID, DISPLAY_OBJECT_KEY, 
				BUCKET_NAME, OBJECT_KEY, E_TAG, TAG_IDS, COLLECTION_IDS, RELATED_CONTENT_IDS, 
				SEQUENCER, ASSET_STATUS, STORAGE_CLASS, ASSET_TYPE, CONTENT_LENGTH,
				STORAGE_EVENT_NAME, CREATED_DATE, STORAGE_SOURCE_IP_ADDRESS,
				START_MEDIA_PROCESSOR, DELETE_MISSING_ASSET, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset registered", sep=" ")

			return REGISTERED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Reprocesses an asset.
	Parameters:
	TARGET_IDS (list of str): The target IDs of the reprocess.
	Returns:
	dict: Returns the information of the reprocessed asset.
	Exception:
	If the asset fails to reprocess.
	If the API type is not admin.
	"""
	def reprocess_asset(self, TARGET_IDS: List[str]) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Reprocessing asset", sep=" ")
			
			REPROCESSED_ASSET_INFO = _reprocess_asset(self.token, 
				self.config["serviceApiUrl"], TARGET_IDS, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset reprocessed", sep=" ")

			return REPROCESSED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Restores an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to restore.
	Returns:
	dict: Returns the information of the restored asset.
	Exception:
	If the asset fails to restore.
	"""
	def restore_asset(self, ASSET_ID: str):
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Restoring asset", sep=" ")

			RESTORED_ASSET_INFO = _restore_asset(self.token, self.config["serviceApiUrl"], 
												 ASSET_ID, self.config["apiType"], 
												 self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset restored", sep=" ")

			return RESTORED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Shares an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to share.
	NOMAD_USERS (list of dict | None): The nomad users of the share. dict format: { id: string }
	EXTERNAL_USERS (list of dict | None): The external users of the share. dict format: { id: string }
	SHARE_DURATION_IN_HOURS (int | None): The share duration in hours of the share.
	Returns:
	dict: Returns the information of the shared asset.
	Exception:
	If the asset fails to share.
	If the API type is not portal.
	"""
	def share_asset(self, ASSET_ID: str, NOMAD_USERS: List[dict] | None, 
				    EXTERNAL_USERS: List[dict] | None, 
					SHARE_DURATION_IN_HOURS: int | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Sharing asset", sep=" ")
			
			SHARED_ASSET_INFO = _share_asset(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, NOMAD_USERS, EXTERNAL_USERS, 
				SHARE_DURATION_IN_HOURS, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset shared", sep=" ")

			return SHARED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Starts a workflow.
	Parameters:
	ACTION_ARGUMENTS (dict): The action arguments of the start. dict format: { "workflowName": {WORKFLOW_NAME} }
	TARGET_IDS (list of str): The target IDs of the start.
	Returns:
	dict: Returns the information of the started workflow.
	Exception:
	If the workflow fails to start.
	If the API type is not admin.
	"""
	def start_workflow(self, ACTION_ARGUMENTS: dict, TARGET_IDS: List[str]) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Starting workflow", sep=" ")
			
			STARTED_WORKFLOW_INFO = _start_workflow(self.token, 
				self.config["serviceApiUrl"], ACTION_ARGUMENTS, TARGET_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Workflow started", sep=" ")

			return STARTED_WORKFLOW_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Transcribes an asset.
	Parameters:
	ASSET_ID (str): The ID of the asset to transcribe.
	TRANSCRIPT_ID (str): The ID of the transcript.
	TRANSCRIPT (list of dict | None): The transcript of the transcribe. dict format: { "startTimeCode": {START_TIME_CODE}, "content": {CONTENT} }
	Returns:
	dict: A promise that resolves when the asset is transcribed.
	Exception:
	If the asset fails to transcribe.
	If the API type is not portal.
	"""
	def transcribe_asset(self, ASSET_ID: str, TRANSCRIPT_ID: str,
					     TRANSCRIPT: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Transcribing asset", sep=" ")
			
			_transcribe_asset(self.token, self.config["serviceApiUrl"], ASSET_ID, 
				TRANSCRIPT_ID, TRANSCRIPT, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset transcribed", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates an annotation.
	Parameters:
	ASSET_ID (str): The ID of the asset to update the annotation for.
	ANNOTATION_ID (str): The ID of the annotation.
	START_TIME_CODE (str | None): The start time code of the annotation. Please use the following format: hh:mm:ss;ff.
	END_TIME_CODE (str | None): The end time code of the annotation. Please use the following format: hh:mm:ss;ff.
	FIRST_KEYWORD (str | None): The first keyword of the annotation.
	SECOND_KEYWORD (str | None): The second keyword of the annotation.
	DESCRIPTION (str | None): The description of the annotation.
	COUNTRY (dict | None): The country of the annotation. dict format: {"id": "string", "description": "string"}
	CONTENT_ID (str |None): The content ID of the annotation.
	IMAGE_URL (str |None): The image URL of the annotation.
	Returns:
	dict: Returns the information of the updated annotation.
	Exception:
	If the annotation fails to create.
	If the API type is not portal.
	"""
	def update_annotation(self, ASSET_ID: str, ANNOTATION_ID: str, START_TIME_CODE: str,
					      END_TIME_CODE: str, FIRST_KEYWORD: str, SECOND_KEYWORD: str,
						  DESCRIPTION: str, COUNTRY: dict, CONTENT_ID: str | None,
						  IMAGE_URL: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Updating annotation", sep=" ")

			UPDATED_ANNOTATION_INFO = _update_annotation(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, ANNOTATION_ID, START_TIME_CODE, END_TIME_CODE, FIRST_KEYWORD, 
				SECOND_KEYWORD, DESCRIPTION, COUNTRY, CONTENT_ID, IMAGE_URL, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Annotation updated", sep=" ")

			return UPDATED_ANNOTATION_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Updates specific properties of the asset. Other API calls can be used to alter other more involved properties.
	Parameters:
	ASSET_ID (str): The ID of the asset to update.
	DISPLAY_NAME (str |None): The display name of the asset.
	DISPLAY_DATE (str |None): The display date of the asset.
	AVAILABLE_START_DATE (str |None): The available start date of the asset.
	AVAILABLE_END_DATE (str |None): The available end date of the asset.
	CUSTOM_PROPERTIES (dict | None): The custom properties of the asset. dict format: {"key": "string", "value": "string"}
	Returns:
	dict: Returns the information of the updated asset.
	Exception:
	If the asset fails to update.
	If the API type is not admin.
	"""
	def update_asset(self, ASSET_ID: str, DISPLAY_NAME: str | None, DISPLAY_DATE: str | None,
				     AVAILABLE_START_DATE: str | None, AVAILABLE_END_DATE: str | None, 
					 CUSTOM_PROPERTIES: dict | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Updating asset", sep=" ")

			UPDATED_ASSET_INFO = _update_asset(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, DISPLAY_NAME, DISPLAY_DATE, AVAILABLE_START_DATE, AVAILABLE_END_DATE, 
				CUSTOM_PROPERTIES, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset updated", sep=" ")

			return UPDATED_ASSET_INFO
		except Exception as error:
			raise Exception(error.args[0])
		

	"""
	Description:
	Updates an asset ad break.
	Parameters:
	ASSET_ID (str): The ID of the asset to update the ad break for.
	AD_BREAK_ID (str): The ID of the ad break.
	TIME_CODE (str |None): The time code of the asset ad break. Please use the following format: hh:mm:ss;ff.
	TAGS (list of dict | None): The tags of the asset ad break. dict format: {"id": "string", "description": "string"}
	LABELS (list of dict | None): The labels of the asset ad break. dict format: {"id": "string", "description": "string"}
	Returns:
	dict: Returns the information of the created asset ad break.
	Exception:
	If the asset ad break fails to create.
	If the API type is not admin.
	"""
	def update_asset_ad_break(self, ASSET_ID: str, AD_BREAK_ID: str, TIME_CODE: str | None, 
						      TAGS: List[dict] | None, LABELS: List[dict] | None) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Updating asset ad break", sep=" ")

			UPDATED_ASSET_AD_BREAK_INFO = _update_asset_ad_break(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, AD_BREAK_ID, TIME_CODE, TAGS, LABELS, 
				self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Asset ad break updated", sep=" ")

			return UPDATED_ASSET_AD_BREAK_INFO
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Updates language of the asset. This will cause a re-process of the AI data.
	Parameters:
	ASSET_ID (str): The ID of the asset to update the language for.
	LANGUAGE_ID (str): The ID of the language.
	Returns:
	dict: Returns the information of the updated asset language.
	Exception:
	If the asset language fails to update.
	If the API type is not admin.
	"""
	def update_asset_language(self, ASSET_ID: str, LANGUAGE_ID: str) -> dict:
		try:
			if self.config["apiType"] != "admin":
				raise Exception("This function is only available for admin API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Updating asset language", sep=" ")

			UPDATED_ASSET_LANGUAGE_INFO = _update_asset_language(self.token, 
				self.config["serviceApiUrl"], ASSET_ID, LANGUAGE_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Asset language updated", sep=" ")

			return UPDATED_ASSET_LANGUAGE_INFO
		except Exception as error:
			raise Exception(error.args[0])

	# Ping
	"""
	Description:
	Pings the user
	Parameters:
	APPLICATION_ID (str | None): The application ID of the user.
	USER_SESSION_ID (str | None): The user session ID of the user.
	Returns:
	dict: The ping status of the user.
	Exception: If ping fails.
	"""
	def ping(self, APPLICATION_ID: str | None, USER_SESSION_ID: str | None) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Pinging user", sep=" ")

			PING_INFO = _ping(self.token, self.config["serviceApiUrl"], 
				APPLICATION_ID, USER_SESSION_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "User pinged", sep=" ")

			return PING_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User failed to ping", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Pings the user
	Parameters:
	APPLICATION_ID (str |None): The application ID of the user.
	USER_SESSION_ID (str): The user session ID of the user.
	Returns:
	dict: The ping status of the user.
	Exception: If ping fails.
	"""
	def ping_auth(self, APPLICATION_ID: str | None, USER_SESSION_ID: str) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Pinging user", sep=" ")

			PING_INFO = _ping_auth(self.token, self.config["serviceApiUrl"], 
				APPLICATION_ID, USER_SESSION_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "User pinged", sep=" ")

			return PING_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "User failed to ping", sep=" ")
			raise Exception(error.args[0])

	# Search
	"""
	Description:
	Search
	Parameters:
	QUERY (str | None): The query is used for free text searching within all of the text of the records.
	This is typically associated to the values entered into a search bar on a website.
	OFFSET (int | None): The pageOffset is a zero based number offset used for paging purposes. 
	If this value is omitted then the marker based paging is used and the return nextPageOffset 
	value will specify a string - rather than a number. You can only use either the zero based page 
	numbers OR the string based page markers, but not both in a single search query and paging.
	SIZE (int | None): The size is a zero based number that represents how many items 
	in the selected page to return
	FILTERS (list of dicts | None): Filters are the primary mechanism for filtering the returned 
    records. There is often more than 1 filter. When 2 or more filters are supplied then there is an 
    implied "**AND**" between each filter.  The name of each filter must match exactly to the name in 
    the output including the appropriate camel-casing.  The operator choices are: (Equals, NotEqual,
    Contains, NotContains, LessThan, GreaterThan, LessThanEquals, snf GreaterThanEquals).
    The value can be either a single value or an array of values. If an array of values is supplied 
    then there is an implied "**OR**" between each value in the array.  NOTE: When filtering by dates, 
    format matters. The appropriate format to use is UTC format such as YYYY-MM-DDTHH:MM:SS.SSSZ.
	List format: [{"fieldName": "string", "operator": "string", "values" : "list | string"} ...]
	SORT_FIELDS (list of dicts | None): The sortFields allows the top level results to be sorted 
	by one or more of the output result fields. The name represents one of the fields in the output 
	and must match exactly including the camel-casing.
	List format: [{"fieldName": "string", "sortType": ("Ascending" | "Descending")} ...]
	SEARCH_RESULT_FIELDS (list of dicts | None): The searchResultFields allows you to specify specific 
	fields that should be returned in the output as well as any children (or related) records that should 
	be also returned. Note that any given searchResultField can contain children also and those fields can 
	contain children. There is no limit to the level of related children to return
	List format: [{"name": "string"} ...]
	SIMILAR_ASSET_ID (str | None): When SimilarAssetId has a value, then the search 
    results are a special type of results and bring back the items that are the most similar to 
    the item represented here. This search is only enabled when Vector searching has been enabled.
    When this has a value, the SearchQuery value and PageOffset values are ignored.
	MIN_SCORE (int | None): Specifies the minimum score to match when returning results. 
    If omitted, the system default will be used - which is usually .65
	EXCLUDE_TOTAL_RECORD_COUNT (bool | None): Normally, the total record count is 
    returned but the query can be made faster if this value is excluded.
	FILTER_BINDER (int | None): The filter binder of the search. 0 = AND, 1 = OR.
	Returns:
	dict: The information of the search.
	Exception: If search fails.
	"""
	def search(self, QUERY: str | None, OFFSET: int | None, SIZE: int | None,
			   FILTERS: List[dict] | None, SORT_FIELDS: List[dict] | None, 
			   SEARCH_RESULT_FIELDS: List[dict] | None, SIMILAR_ASSET_ID: str | None, 
			   MIN_SCORE: int | None, EXCLUDE_TOTAL_RECORD_COUNT: bool | None, 
			   FILTER_BINDER: int | None) -> dict:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start search", sep=" ")

			IS_ADMIN = self.config["apiType"] == "admin"

			SEARCH_INFO = _post_search(self.token, self.config["serviceApiUrl"], QUERY, OFFSET, SIZE, 
				FILTERS, SORT_FIELDS, SEARCH_RESULT_FIELDS, SIMILAR_ASSET_ID, MIN_SCORE, 
				EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER, IS_ADMIN, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Search complete", sep=" ")

			return SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Search failed", sep=" ")
			raise Exception(error.args[0])
		
	# Portal
	"""
	Description:
	Changes the email of the user.
	Parameters:
	NEW_EMAIL (str): The new email of the user.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If change email fails.
	"""
	def change_email(self, NEW_EMAIL: str)-> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start change email", sep=" ")

			_change_email(self.token, self.config["serviceApiUrl"], NEW_EMAIL,
				          self.config["passowrd"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Change email complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Change email failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Changes the password of the user.
	Parameters:
	NEW_PASSWORD (str): The new password of the user.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If change password fails.
	"""
	def change_password(self, NEW_PASSWORD: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start change password", sep=" ")

			_change_password(self.token, self.config["serviceApiUrl"], 
							 self.config["password"], NEW_PASSWORD, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Change password complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Change password failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets user.
	Parameters:
	None
	Returns:
	dict: The information of the user.
	Exception: If the API type is not portal.
	Exception: If get user fails.
	"""
	def get_user(self) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get user", sep=" ")

			USER_INFO = _get_user(self.token, self.config["serviceApiUrl"], self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get user complete", sep=" ")

			return USER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get user failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updated user.
	Parameters:
	ADDRESS (str | None): The address of the user.
	ADDRESS2 (str | None): The address2 of the user.
	CITY (str | None): The city of the user.
	FIRST_NAME (str | None): The first name of the user.
	LAST_NAME (str | None): The last name of the user.
	PHONE_NUMBER (str | None): The phone number of the user.
	PHONE_EXTENTION (str | None): The phone extention of the user.
	POSTAL_CODE (str | None): The postal code of the user.
	ORGANIZATION (str | None): The organization of the user.
	COUNTRY (str | None): The country of the user.
	STATE (str | None): The state of the user.
	Returns:
	Updated user information.
	Exception: If the API type is not portal.
	Exception: If update user fails.
	"""
	def update_user(self, ADDRESS: str | None, ADDRESS2: str | None, CITY: str | None,
				    FIRST_NAME: str | None, LAST_NAME: str | None, PHONE_NUMBER: str | None, 
					PHONE_EXTENTION: str | None, POSTAL_CODE: str | None, 
					ORGANIZATION: str | None, COUNTRY: str | None, STATE: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start update user", sep=" ")

			USER_INFO = _update_user(self.token, self.config["serviceApiUrl"], ADDRESS, ADDRESS2, 
				CITY, FIRST_NAME, LAST_NAME, PHONE_NUMBER, PHONE_EXTENTION, POSTAL_CODE, 
				ORGANIZATION, COUNTRY, STATE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Update user complete", sep=" ")

			return USER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update user failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Add contents to content group.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	CONTENT_IDS (list of str): The IDs of the content.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If add contents to content group fails.
	"""
	def add_contents_to_content_group(self, CONTENT_GROUP_ID: str, CONTENT_IDS: List[str]) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start add contents to content group", sep=" ")

			INFO = _add_contents_to_content_group(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, CONTENT_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Add contents to content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add contents to content group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Creates a content group.
	Parameters:
	NAME (str): The name of the content group.
	Returns:
	dict: The information of the content group.
	Exception: If the API type is not portal.
	Exception: If create content group fails.
	"""
	def create_content_group(self, NAME: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start create content group", sep=" ")

			CONTENT_GROUP_INFO = _create_content_group(self.token, self.config["serviceApiUrl"], 
				NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create content group complete", sep=" ")

			return CONTENT_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create content group failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a content group.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If delete content group fails.
	"""
	def delete_content_group(self, CONTENT_GROUP_ID: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start delete content group", sep=" ")

			INFO = _delete_content_group(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete content group failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets a content group.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	Returns:
	dict: The information of the content group.
	Exception: If the API type is not portal.
	Exception: If get content group fails.
	"""
	def get_content_group(self, CONTENT_GROUP_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get content group", sep=" ")

			CONTENT_GROUP_INFO = _get_content_group(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get content group complete", sep=" ")

			return CONTENT_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content group failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets all content groups.
	Parameters:
	None
	Returns:
	dict: The information of the content groups.
	Exception: If the API type is not portal.
	Exception: If get content groups fails.
	"""
	def get_content_groups(self) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get content groups", sep=" ")

			CONTENT_GROUP_INFO = _get_content_groups(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get content groups complete", sep=" ")

			return CONTENT_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content groups failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets portal groups.
	Parameters:
	PORTAL_GROUPS (list of str): The portal groups to get. The portal groups are
	contentGroups, sharedContentGroups, and savedSearches. You can only see a content
	groups if it is shared with you, or if you are the owner of the content group.
	Returns:
	dict: The information of the portal groups.
	Exception: If the API type is not portal.
	Exception: If get portal groups fails.
	"""
	def get_portal_groups(self, PORTAL_GROUPS: List[str]) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get portal groups", sep=" ")

			PORTAL_GROUPS_INFO = _get_portal_groups(self.token, self.config["serviceApiUrl"], 
				PORTAL_GROUPS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get portal groups complete", sep=" ")

			return PORTAL_GROUPS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get portal groups failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Removes contents from content group.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	CONTENT_IDS (list of str): The IDs of the content.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If remove contents from content group fails.
	"""
	def remove_contents_from_content_group(self, CONTENT_GROUP_ID: str,
										   CONTENT_IDS: List[str]) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start remove contents from content group", sep=" ")

			INFO = _remove_contents_from_content_group(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, CONTENT_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Remove contents from content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Remove contents from content group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Renames a content group.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	NAME (str): The name of the content group.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If rename content group fails.
	"""
	def rename_content_group(self, CONTENT_GROUP_ID: str, NAME: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start rename content group", sep=" ")

			INFO = _rename_content_group(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, NAME, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Rename content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Rename content group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Shares a content group with users. To share a content group with a user, the 
    user must meet certain requirements. They must not be a guest user and their account must be 
    in a normal state. Only the owner, the user who created the content group, can share the 
    content group. The user the content group is being shared with cannot change the collection.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	USER_IDS (list of str): The IDs of the users.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If share content group fails.
	"""
	def share_content_group_with_user(self, CONTENT_GROUP_ID: str, USER_IDS: List[str]) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start share content group", sep=" ")

			INFO = _share_content_group_with_user(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, USER_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Share content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Share content group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Unshares a content group with users.
	Parameters:
	CONTENT_GROUP_ID (str): The ID of the content group.
	USER_IDS (list): The IDs of the users.
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If unshare content group fails.
	"""
	def stop_sharing_content_group_with_user(self, CONTENT_GROUP_ID: str,
										     USER_IDS: List[str]) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start unshare content group", sep=" ")

			INFO = _stop_sharing_content_group_with_user(self.token, self.config["serviceApiUrl"], 
				CONTENT_GROUP_ID, USER_IDS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Unshare content group complete", sep=" ")

			return INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Unshare content group failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Invites a guest.
	Parameters:
	CONTENT_ID (str | None): The ID of the content to be shared to the user.
	CONTENT_DEFINITION_ID (str | None): The ID of the content definition to be shared to the user.
	EMAILS (list of str): The email(s) of the guest(s).
	CONTENT_SECURITY_ATTRIBUTE (str): The content security attribute of the guest.
    The content security attribute can be "Undefined", "Guest", or "Demo".
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If invite guest fails.
	"""
	def guest_invite(self, CONTENT_ID: str | None, CONTENT_DEFINITION_ID: str | None, 
				     EMAILS: List[str], CONTENT_SECURITY_ATTRIBUTE: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start invite guest", sep=" ")

			_guest_invite(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, self.id, EMAILS, CONTENT_SECURITY_ATTRIBUTE, 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Invite guest complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Invite guest failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Register a guest.
	Parameters:
	EMAIL (str): The email of the guest.
	FIRST_NAME (str | None): The first name of the guest.
	LAST_NAME (str | None): The last name of the guest.
	PASSWORD (str): The password of the guest.
	Returns:
	dict: The information of the guest.
	Exception: If the API type is not portal.
	Exception: If register guest fails.
	"""
	def register_guest(self, EMAIL: str, FIRST_NAME: str | None, LAST_NAME: str | None,
					   PASSWORD: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start register guest", sep=" ")

			GUEST_INFO = _register_guest(self.token, self.config["serviceApiUrl"], EMAIL, 
				FIRST_NAME, LAST_NAME, PASSWORD, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Register guest complete", sep=" ")

			return GUEST_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Register guest failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Removes a guest.
	Parameters:
	CONTENT_ID (str | None): The ID of the content to be unshared to the user.
	CONTENT_DEFINITION_ID (str | None): The ID of the content definition to be unshared to the user.
	EMAILS (list of str): The email(s) of the guest(s).
	CONTENT_SECURITY_ATTRIBUTE (str): The content security attribute of the guest.
	The content security attribute can be "Undefined", "Guest", or "Demo".
	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If remove guest fails.
	"""
	def remove_guest(self, CONTENT_ID: str | None, CONTENT_DEFINITION_ID: str | None,
				     EMAILS: List[str], CONTENT_SECURITY_ATTRIBUTE: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start remove guest", sep=" ")

			_remove_guest(self.token, self.config["serviceApiUrl"], CONTENT_ID, 
				CONTENT_DEFINITION_ID, self.id, EMAILS, CONTENT_SECURITY_ATTRIBUTE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Remove guest complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Remove guest failed", sep=" ")
			raise Exception(error.args[0])

	# Media
	"""
	Description:
	Delete continue watching markers.
	Parameters:
	USER_ID (str |None): The user ID of the user to clear the continue watching list. If no user Id is passed it clears the markers of the logged in user.
	ASSET_ID (str |None): The asset ID of the asset to clear the continue watching list. If no asset Id is passed it clears the markers of all assets.
	Returns:
	None
	Exception:
	If the continue watching list fails to clear.
	If the API type is not portal.
	"""
	def clear_continue_watching(self, USER_ID: str | None, ASSET_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Clear continue watching", sep=" ")

			USER_ID = USER_ID if USER_ID else self.id

			_clear_continue_watching(self.token, self.config["serviceApiUrl"], USER_ID, ASSET_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Clear continue watching complete", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Clears the watchlist.
	Parameters:
	USER_ID (str |None): The user ID of the user to clear the watchlist. If no user Id is passed it clears the watchlist of the logged in user.
	Returns:
	None
	Exception:
	If the watchlist fails to clear.
	If the API type is not portal.
	"""
	def clear_watchlist(self, USER_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Clear watchlist", sep=" ")

			USER_ID = USER_ID if USER_ID else self.id

			_clear_watchlist(self.token, self.config["serviceApiUrl"], USER_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Clear watchlist complete", sep=" ")
		except Exception as error:
			raise Exception(error.args[0])

	"""
	Description:
	Creates a form.
	Parameters:
	CONTENT_DEFINITION_ID (str): The id of the content definition the form
	is going in.
	FORM_INFO (dict): The information of the form.
	Returns:
	dict: The id of the form.
	Exception: If the API type is not portal.
	Exception: If create form fails.
	"""
	def create_form(self, CONTENT_DEFINITION_ID: str, FORM_INFO: dict) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start create form", sep=" ")

			FORM_ID = _create_form(self.token, self.config["serviceApiUrl"], 
				CONTENT_DEFINITION_ID, FORM_INFO, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Create form complete", sep=" ")

			return FORM_ID
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create form failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets content cookies.
	Parameters:
	CONTENT_ID (str): The Id of the content to retrieve the cookies for. This can be the ID for the content definition of the LiveChannel, or a folder asset ID or a specific Asset ID.
	Returns:
	dict: Returns the information of the gotten content cookies.
	Exception:
	If the content cookies fail to get.
	If the API type is not portal.
	"""
	def get_content_cookies(self, CONTENT_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get content cookies", sep=" ")

			CONTENT_COOKIES_INFO = _get_content_cookies(self.token, self.config["serviceApiUrl"], 
				CONTENT_ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Get content cookies complete", sep=" ")

			return CONTENT_COOKIES_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get content cookies failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets default site config.
	Returns:
	list[dict]: Returns the information of the gotten dynamic content.
	Exception:
	If the dynamic content fails to get.
	If the API type is not portal.
	"""
	def get_default_site_config(self) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get default site config", sep=" ")

			DEFAULT_SITE_CONFIG_INFO = _get_default_site_config(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get default site config complete", sep=" ")

			return DEFAULT_SITE_CONFIG_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get default site config failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets dynamic content.
	Parameters:
	DYNAMIC_CONTENT_RECORD_ID (str): The dynamic content record ID.
	Returns:
	dict: Returns the information of the gotten dynamic content.
	Exception:
	If the dynamic content fails to get.
	If the API type is not portal.
	"""
	def get_dynamic_content(self, DYNAMIC_CONTENT_RECORD_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get dynamic content", sep=" ")

			DYNAMIC_CONTENT_INFO = _get_dynamic_content(self.token, self.config["serviceApiUrl"], 
				DYNAMIC_CONTENT_RECORD_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get dynamic content complete", sep=" ")

			return DYNAMIC_CONTENT_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get dynamic content failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets dynamic contents.
	Returns:
	list[dict]: Returns the information of the gotten dynamic content.
	Exception:
	If the dynamic content fails to get.
	If the API type is not portal.
	"""
	def get_dynamic_contents(self) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get dynamic contents", sep=" ")

			DYNAMIC_CONTENTS_INFO = _get_dynamic_contents(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get dynamic contents complete", sep=" ")

			return DYNAMIC_CONTENTS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get dynamic contents failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets media group.
	Parameters:
	MEDIA_GROUP_ID (str): The ID of the media group.
	Returns:
	dict: Returns the information of the gotten media group.
	Exception:
	If the media group fails to get.
	If the API type is not portal.
	"""
	def get_media_group(self, MEDIA_GROUP_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get media", sep=" ")

			MEDIA_INFO = _get_media_group(self.token, self.config["serviceApiUrl"], 
				MEDIA_GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media complete", sep=" ")

			return MEDIA_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets media item.
	Parameters:
	MEDIA_ITEM_ID (str): The ID of the media item.
	Returns:
	dict: Returns the information of the gotten media item.
	Exception:
	If the media item fails to get.
	If the API type is not portal.
	"""
	def get_media_item(self, MEDIA_ITEM_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get media", sep=" ")

			MEDIA_INFO = _get_media_item(self.token, self.config["serviceApiUrl"], 
				MEDIA_ITEM_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media complete", sep=" ")

			return MEDIA_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets favorites and continue watching lists of IDs for the logged in user.
	Returns:
	dict: Returns the information of the gotten favorites and continue watching lists of IDs.
	Exception:
	If the favorites and continue watching lists of IDs fail to get.
	If the API type is not portal.
	"""
	def get_my_content(self) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			MY_MEDIA_IDS_INFO = _get_my_content(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			return MY_MEDIA_IDS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get my media IDs failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets user's group.
	Parameters:
	GROUP_ID (str): The ID of the group.
	Returns:
	dict: Returns the information of the gotten user's group.
	Exception:
	If the user's group fails to get.
	If the API type is not portal.
	"""
	def get_my_group(self, GROUP_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get user group", sep=" ")

			USER_GROUP_INFO = _get_my_group(self.token, self.config["serviceApiUrl"], 
				GROUP_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get user group complete", sep=" ")

			return USER_GROUP_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get user group failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets site config.
	Parameters:
	SITE_CONFIG_RECORD_ID (str): The site config record ID.
	Returns:
	dict: Returns the information of the gotten site config.
	Exception:
	If the site config fails to get.
	If the API type is not portal.
	"""
	def get_site_config(self, SITE_CONFIG_RECORD_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get site config", sep=" ")

			SITE_CONFIG_INFO = _get_site_config(self.token, self.config["serviceApiUrl"], 
				SITE_CONFIG_RECORD_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get site config complete", sep=" ")

			return SITE_CONFIG_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get site config failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Searches for media.
	Parameters:
	QUERY (str | None): The query of the search.
	IDS (list of str | None): The ids of the media to be searched.
	SORT_FIELDS (list of dict | None): The sort fields of the search. [{"fieldName": "string", "sortType": ("Ascending" | "Descending")} ...]
	"Ascending" or "Descending".
	OFFSET (int | None): The offset of the search.
	SIZE (int | None): The size of the search.
	Returns:
	dict: The information of the search.
	Exception: If the API type is not portal.
	Exception: If search media fails.
	"""
	def media_search(self, QUERY: str | None, IDS: List[str] | None, SORT_FIELDS: List[dict], 
				     OFFSET: int | None, SIZE: int | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start search media", sep=" ")

			SEARCH_INFO = _media_search(self.token, self.config["serviceApiUrl"], 
				QUERY, IDS, SORT_FIELDS, OFFSET, SIZE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Search media complete", sep=" ")

			return SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Search media failed", sep=" ")
			raise Exception(error.args[0])
		
	# Media Builder
	"""
	Description:
	Creates a media builder.

	Parameters:
	NAME (str): The name of the media builder.
	DESTINATION_FOLDER_ID (str | None): The ID of the destination folder.
	COLLECTIONS (list of str | None): The collections of the media builder.
	RELATED_CONTENTS (list of str | None): The related contents of the media builder.
	TAGS: (list of str | None): The tags of the media builder.
	PROPERTIES (dict | None): The properties of the media builder. {"string": "string" ...}
	Returns 
	dict: The information of the media builder.
	Exception: If the API type is not portal.
	Exception: If create media builder fails.
	"""
	def create_media_builder(self, NAME: str, DESTINATION_FOLDER_ID: str | None,
							 COLLECTIONS: List[str] | None, 
							 RELATED_CONTENTS: List[str] | None,
							 TAGS: List[str] | None,
							 PROPERTIES: dict | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start create media builder", sep=" ")

			MEDIA_BUILDER_INFO = _create_media_builder(self.token,
				self.config["serviceApiUrl"], NAME, DESTINATION_FOLDER_ID, COLLECTIONS,
				RELATED_CONTENTS, TAGS, PROPERTIES, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create media builder complete", sep=" ")

			return MEDIA_BUILDER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create media builder failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Creates a media builder item.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	SOURCE_ASSET_ID (str | None): The ID of the source asset.
	START_TIME_CODE (str | None): The start time code of the media builder item. Only use if using source asset.
	END_TIME_CODE (str | None): The end time code of the media builder item. Only use if using source asset.
	SOURCE_ANNOTATION_ID (str | None): The ID of the source annotation. Only use if using source annotation.
	RELATED_CONTENTS (list of str | None): The related contents of the media builder item.

	Returns:
	dict: The information of the media builder item.
	Exception: If the API type is not portal.
	Exception: If create media builder item fails.
	"""
	def create_media_builder_item(self, MEDIA_BUILDER_ID: str, SOURCE_ASSET_ID: str | None,
								  START_TIME_CODE: str | None, END_TIME_CODE: str | None,
								  SOURCE_ANNOTATION_ID: str | None, RELATED_CONTENTS: List[str] | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start create media builder item", sep=" ")

			MEDIA_BUILDER_ITEM_INFO = _create_media_builder_item(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, SOURCE_ASSET_ID, START_TIME_CODE, END_TIME_CODE, SOURCE_ANNOTATION_ID, 
				RELATED_CONTENTS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create media builder item complete", sep=" ")

			return MEDIA_BUILDER_ITEM_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create media builder item failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Creates media builder items from annotations

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	SOURCE_ASSET_ID (str): The ID of the source asset.

	Returns:
	list[dict]: The information of the media builder items.
	Exception: If the API type is not portal.
	Exception: If create media builder items from annotations fails.
	"""
	def create_media_builder_items_add_annotations(self, MEDIA_BUILDER_ID: str, SOURCE_ASSET_ID: str) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start create media builder items from annotations", sep=" ")

			MEDIA_BUILDER_ITEMS_INFO = _create_media_builder_items_add_annotations(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, SOURCE_ASSET_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create media builder items from annotations complete", sep=" ")

			return MEDIA_BUILDER_ITEMS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create media builder items from annotations failed", sep=" ")
			raise Exception(error.args[0])
		
	""" 
	Description:
	Creates media builder items in bulk

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	MEDIA_BUILDER_ITEMS (list of dict): The list of media builder items.
	Format: [{"sourceAssetId": "string", "sourceAnnotationId": "string | null",
    "startTimeCode": "string | null", "endTimeCode": "string | null"}]
	"""
	def create_media_builder_items_bulk(self, MEDIA_BUILDER_ID: str, MEDIA_BUILDER_ITEMS: List[dict]) -> None:
		try:
			print(datetime.now().strftime('%H:%M:%S'), "Start create media builder items in bulk", sep=" ")

			MEDIA_BUILDER_ITEMS_INFO = _create_media_builder_items_bulk(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, MEDIA_BUILDER_ITEMS, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Create media builder items in bulk complete", sep=" ")

			return MEDIA_BUILDER_ITEMS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Create media builder items in bulk failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a media builder.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.

	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If delete media builder fails.
	"""
	def delete_media_builder(self, MEDIA_BUILDER_ID: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start delete media builder", sep=" ")

			_delete_media_builder(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete media builder complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete media builder failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a media builder item.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	MEDIA_BUILDER_ITEM_ID (str): The ID of the media builder item.

	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If delete media builder item fails.
	"""
	def delete_media_builder_item(self, MEDIA_BUILDER_ID: str, MEDIA_BUILDER_ITEM_ID: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start delete media builder item", sep=" ")

			_delete_media_builder_item(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, MEDIA_BUILDER_ITEM_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete media builder item complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete media builder item failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Duplicates a media builder.
	
	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	NAME (str): The name of the media builder.
	DESTINATION_FOLDER_ID (str | None): The ID of the destination folder.
	COLLECTIONS (list of str | None): The collections of the media builder.
	RELATED_CONTENTS (list of str | None): The related contents of the media builder.
	PROPERTIES (dict | None): The properties of the media builder. {"string": "string" ...}

	Returns:
	dict: The information of the duplicated media builder.
	Exception: If the API type is not portal.
	Exception: If duplicate media builder fails.
	"""
	def duplicate_media_builder(self, MEDIA_BUILDER_ID: str, NAME: str, 
							 	DESTINATION_FOLDER_ID: str | None, 
								COLLECTIONS: List[str] | None,
								RELATED_CONTENTS: List[str] | None,
								PROPERTIES: dict | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start duplicate media builder", sep=" ")

			DUPLICATED_MEDIA_BUILDER_INFO = _duplicate_media_builder(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, NAME, DESTINATION_FOLDER_ID, COLLECTIONS, RELATED_CONTENTS, PROPERTIES, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Duplicate media builder complete", sep=" ")

			return DUPLICATED_MEDIA_BUILDER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Duplicate media builder failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets a media builder.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.

	Returns:
	dict: The information of the gotten media builder.
	Exception: If the API type is not portal.
	Exception: If get media builder fails.
	"""
	def get_media_builder(self, MEDIA_BUILDER_ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start get media builder", sep=" ")

			MEDIA_BUILDER_INFO = _get_media_builder(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media builder complete", sep=" ")

			return MEDIA_BUILDER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media builder failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets media builder ids from a given asset.

	Parameters:
	SOURCE_ASSET_ID (str): The ID of the source asset.

	Returns:
	list[str]: The information of the gotten media builder ids.
	Exception: If the API type is not portal.
	Exception: If get media builder item ids fails.
	"""
	def get_media_builder_ids_from_asset(self, SOURCE_ASSET_ID: str) -> list[str]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start get media builder item ids from asset", sep=" ")

			MEDIA_BUILDER_ITEM_IDS_INFO = _get_media_builder_ids_from_asset(self.token, 
				self.config["serviceApiUrl"], SOURCE_ASSET_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media builder item ids from asset complete", sep=" ")

			return MEDIA_BUILDER_ITEM_IDS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media builder item ids from asset failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets media builders

	Returns:
	list[dict]: The information of the gotten media builders.
	Exception: If the API type is not portal.
	Exception: If get media builders fails.
	"""
	def get_media_builders(self) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start get media builders", sep=" ")

			MEDIA_BUILDERS_INFO = _get_media_builders(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media builders complete", sep=" ")

			return MEDIA_BUILDERS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media builders failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets media builder items.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.

	Returns:
	list[dict]: The information of the gotten media builder items.
	Exception: If the API type is not portal.
	Exception: If get media builder items fails.
	"""
	def get_media_builder_items(self, MEDIA_BUILDER_ID) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start get media builder items", sep=" ")

			MEDIA_BUILDER_ITEMS_INFO = _get_media_builder_items(self.token, 
				self.config["serviceApiUrl"], MEDIA_BUILDER_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get media builder items complete", sep=" ")

			return MEDIA_BUILDER_ITEMS_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get media builder items failed", sep=" ")
			raise Exception(error.args[0])
		
		
	"""
	Description:
	Moves a media builder item.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	MEDIA_BUILDER_ITEM_ID (str): The ID of the media builder item.
	MEDIA_BUILDER_PREVIOUS_ITEM_ID (str | None): The ID of the media builder previous item.

	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If move media builder item fails.
	"""

	def move_media_builder_item(self, MEDIA_BUILDER_ID: str, MEDIA_BUILDER_ITEM_ID: str,
								MEDIA_BUILDER_PREVIOUS_ITEM_ID: str | None) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			_move_media_builder_item(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, MEDIA_BUILDER_ITEM_ID, MEDIA_BUILDER_PREVIOUS_ITEM_ID, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "Move media builder item complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Move media builder item failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Renders a media builder.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.

	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If render media builder fails.
	"""
	def render_media_builder(self, MEDIA_BUILDER_ID: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			print(datetime.now().strftime('%H:%M:%S'), "Start render media builder", sep=" ")

			RENDER_INFO =_render_media_builder(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Render media builder complete", sep=" ")
			return RENDER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Render media builder failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Updates a media builder.

	Parameters:
	MEDIA_BUILDER_ID (str): The ID of the media builder.
	NAME (str | None): The name of the media builder.
	DESTINATION_FOLDER_ID (str | None): The ID of the destination folder.
	COLLECTIONS (list of str | None): The collections of the media builder.
	RELATED_CONTENTS (list of str | None): The related contents of the media builder.
	TAGS (list of str | None): The tags of the media builder.
	PROPERTIES (dict | None): The properties of the media builder. {"string": "string" ...}

	Returns:
	None
	Exception: If the API type is not portal.
	Exception: If update media builder fails.
	"""
	def update_media_builder(self, MEDIA_BUILDER_ID: str, NAME: str | None,
							 DESTINATION_FOLDER_ID: str | None, COLLECTIONS: List[str] | None,
							 RELATED_CONTENTS: List[str] | None, TAGS: List[str] | None,
							 PROPERTIES: dict | None) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")

			print(datetime.now().strftime('%H:%M:%S'), "Start update media builder", sep=" ")

			BUILDER_INFO = _update_media_builder(self.token, self.config["serviceApiUrl"], 
				MEDIA_BUILDER_ID, NAME, DESTINATION_FOLDER_ID, COLLECTIONS, RELATED_CONTENTS, 
				TAGS, PROPERTIES, self.debug_mode)
			print(datetime.now().strftime('%H:%M:%S'), "Update media builder complete", sep=" ")
			return BUILDER_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update media builder failed", sep=" ")
			raise Exception(error.args[0])

	# Saved Search
	"""
	Description:
	Adds a saved search.

	Parameters:
	NAME (str): The name of the saved search.
	FEATURED (bool | None): If the saved search is featured.
	BOOKMARKED (bool | None): If the saved search is bookmarked.
	PUBLIC (bool | None): If the saved search is public.
	SEQUENCE (int | None): The sequence of the saved search.
	TYPE (int | None): The type of the saved search. 0 = List, 1 = Preview Image, 2 = Header.
	QUERY (str | None): The query of the search.
	OFFSET (int | None): The offset of the search.
	SIZE (int | None): The size of the search.
	FILTERS (list of dict | None): The filters of the search. [{"fieldName": "string", "operator": "string", "values" : "list of string"} ...]
	SORT_FIELDS (list of dict | None): The sort fields of the search. [{"fieldName": "string", "sortType": ("Ascending" | "Descending")} ...]
	SEARCH_RESULT_FIELDS (list of dict | None): The property fields you want to show in the result. [{"name": "string"} ...]
	SIMILAR_ASSET_ID (str | None): When SimilarAssetId has a value, then the search results are a special type of results and bring back the items that are the most similar to the item represented here. This search is only enabled when Vector searching has been enabled. When this has a value, the SearchQuery value and PageOffset values are ignored.
	MIN_SCORE (float | None): Specifies the minimum score to match when returning results. If omitted, the system default will be used - which is usually .65
	EXCLUDE_TOTAL_RECORD_COUNT (bool | None): Normally, the total record count is returned but the query can be made faster if this value is excluded.
	FILTER_BINDER (str | None): The filter binder of the search. 0 = AND, 1 = OR.

	Returns:
	dict: Returns the information of the added saved search.

	Exception: If the API type is not portal.
	Exception: If the saved search fails to add.
	"""
	def add_saved_search(self, NAME: str, FEATURED: bool, BOOKMARKED: bool, PUBLIC: bool | None,
					     SEQUENCE: int | None, TYPE: int | None, QUERY: str | None,
					  	 OFFSET: int | None, SIZE: int | None, FILTERS: List[dict] | None, 
						 SORT_FIELDS: List[dict] | None, SEARCH_RESULT_FIELDS: List[dict] | None,
						 SIMILAR_ASSET_ID: str | None, MIN_SCORE: float | None, 
						 EXCLUDE_TOTAL_RECORD_COUNT: bool | None, FILTER_BINDER: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start add saved search", sep=" ")

			SAVED_SEARCH_INFO = _add_saved_search(self.token, self.config["serviceApiUrl"], 
				NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, TYPE, QUERY, OFFSET, SIZE, FILTERS, 
				SORT_FIELDS, SEARCH_RESULT_FIELDS, SIMILAR_ASSET_ID, MIN_SCORE, 
				EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Add saved search complete", sep=" ")

			return SAVED_SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Add saved search failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Deletes a saved search.

	Parameters:
	ID (str): The ID of the saved search.

	Returns:
	None

	Exception: If the API type is not portal.
	Exception: If the saved search fails to delete.
	"""
	def delete_saved_search(self, ID: str) -> None:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start delete saved search", sep=" ")

			_delete_saved_search(self.token, self.config["serviceApiUrl"], ID, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Delete saved search complete", sep=" ")
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Delete saved search failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets a saved search.

	Parameters:
	ID (str): The ID of the saved search.

	Returns:
	dict: Returns the information of the gotten saved search.

	Exception: If the API type is not portal.
	Exception: If the saved search fails to get.
	"""
	def get_saved_search(self, ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get saved search", sep=" ")

			SAVED_SEARCH_INFO = _get_saved_search(self.token, self.config["serviceApiUrl"], 
				ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Get saved search complete", sep=" ")

			return SAVED_SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get saved search failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Gets saved searches.

	Parameters:
	None

	Returns:
	list[dict]: Returns the information of the gotten saved searches.

	Exception: If the API type is not portal.
	Exception: If the saved searches fails to get.
	"""
	def get_saved_searches(self) -> list[dict]:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get saved searches", sep=" ")

			SAVED_SEARCHES_INFO = _get_saved_searches(self.token, self.config["serviceApiUrl"], 
				self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get saved searches complete", sep=" ")

			return SAVED_SEARCHES_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get saved searches failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Gets search saved based on params.

	Parameters:
	QUERY (str | None): The query of the search.
	OFFSET (int | None): The offset of the search.
	SIZE (int | None): The size of the search.
	FILTERS (list of dict | None): The filters of the search. [{"fieldName": "string", "operator": "string", "values" : "array<string>" | "string"} ...]
	SORT_FIELDS (list of dict | None): The sort fields of the search. [{"fieldName": "string", "sortType": ("Ascending" | "Descending")} ...]
	SEARCH_RESULT_FIELDS (list of dict | None): The property fields you want to show in the result. [{"name": "string"} ...]
	SIMILAR_ASSET_ID (str | None): When SimilarAssetId has a value, then the search results are a special type of results and bring back the items that are the most similar to the item represented here. This search is only enabled when Vector searching has been enabled. When this has a value, the SearchQuery value and PageOffset values are ignored.
	MIN_SCORE (float | None): Specifies the minimum score to match when returning results. If omitted, the system default will be used - which is usually .65
	EXCLUDE_TOTAL_RECORD_COUNT (bool | None): Normally, the total record count is returned but the query can be made faster if this value is excluded.
	FILTER_BINDER (str | None): The filter binder of the search. 0 = AND, 1 = OR.

	Returns:
	dict: Returns the information of the search saved.

	Exception: If the API type is not portal.
	Exception: If the search saved fails to get.
	"""
	def get_search_saved(self, QUERY: str | None, OFFSET: int | None, SIZE: int | None, 
					     FILTERS: List[dict] | None, SORT_FIELDS: List[dict] | None, 
						 SEARCH_RESULT_FIELDS: List[dict] | None, SIMILAR_ASSET_ID: str | None,
						 MIN_SCORE: float | None, EXCLUDE_TOTAL_RECORD_COUNT: bool | None,
						 FILTER_BINDER: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get search saved", sep=" ")

			SEARCH_SAVED_INFO = _get_search_saved(self.token, self.config["serviceApiUrl"], 
				QUERY, OFFSET, SIZE, FILTERS, SORT_FIELDS, SEARCH_RESULT_FIELDS, SIMILAR_ASSET_ID, 
				MIN_SCORE, EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Get search saved complete", sep=" ")

			return SEARCH_SAVED_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get search saved failed", sep=" ")
			raise Exception(error.args[0])	

	"""
	Description:
	Gets search saved by id

	Parameters:
	ID (str): The ID of the search saved.

	Returns:
	dict: Returns the information of the search saved.

	Exception: If the API type is not portal.
	Exception: If the search saved fails to get.
	"""			
	def get_search_saved_by_id(self, ID: str) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get search saved", sep=" ")

			SEARCH_SAVED_INFO = _get_search_saved_by_id(self.token, self.config["serviceApiUrl"], 
				ID, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Get search saved complete", sep=" ")

			return SEARCH_SAVED_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get search saved failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Patches a saved search.

	Parameters:
	ID (str): The ID of the saved search.
	NAME (str | None): The name of the saved search.
	FEATURED (bool | None): If the saved search is featured.
	BOOKMARKED (bool | None): If the saved search is bookmarked.
	PUBLIC (bool | None): If the saved search is public.
	SEQUENCE (int | None): The sequence of the saved search.

	Returns:
	dict: Returns the information of the patched saved search.

	Exception: If the API type is not portal.
	Exception: If the saved search fails to patch.
	"""
	def patch_saved_search(self, ID: str, NAME: str | None, FEATURED: bool | None, 
						   BOOKMARKED: bool | None, PUBLIC: bool | None, 
						   SEQUENCE: int | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start patch saved search", sep=" ")

			SAVED_SEARCH_INFO = _patch_saved_search(self.token, self.config["serviceApiUrl"], 
				ID, NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, self.debug_mode)

			print(datetime.now().strftime('%H:%M:%S'), "Patch saved search complete", sep=" ")

			return SAVED_SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Patch saved search failed", sep=" ")
			raise Exception(error.args[0])
		
	"""
	Description:
	Updates a saved search.

	Parameters:
	ID (str): The ID of the saved search.
	NAME (str | None): The name of the saved search.
	FEATURED (bool | None): If the saved search is featured.
	BOOKMARKED (bool | None): If the saved search is bookmarked.
	PUBLIC (bool | None): If the saved search is public.
	SEQUENCE (int | None): The sequence of the saved search.
	TYPE (int | None): The type of the saved search. 0 = List, 1 = Preview Image, 2 = Header.
	QUERY (str | None): The query of the search.
	OFFSET (int | None): The offset of the search.
	SIZE (int | None): The size of the search.
	FILTERS (list of dict | None): The filters of the search. [{"fieldName": "string", "operator": "string", "values" : "array<string>" | "string"} ...]
	SORT_FIELDS (list of dict | None): The sort fields of the search. [{"fieldName": "string", "sortType": ("Ascending" | "Descending")} ...]
	SEARCH_RESULT_FIELDS (list of dict | None): The property fields you want to show in the result. [{"name": "string"} ...]
	SIMILAR_ASSET_ID (str | None): When SimilarAssetId has a value, then the search results are a special type of results and bring back the items that are the most similar to the item represented here. This search is only enabled when Vector searching has been enabled. When this has a value, the SearchQuery value and PageOffset values are ignored.
	MIN_SCORE (float | None): Specifies the minimum score to match when returning results. If omitted, the system default will be used - which is usually .65
	EXCLUDE_TOTAL_RECORD_COUNT (bool | None): Normally, the total record count is returned but the query can be made faster if this value is excluded.
	FILTER_BINDER (str | None): The filter binder of the search. 0 = AND, 1 = OR.

	Returns:
	dict: Returns the information of the updated saved search.

	Exception: If the API type is not portal.
	Exception: If the saved search fails to update.
	"""
	def update_saved_search(self, ID: str, NAME: str | None, FEATURED: bool | None, 
						    BOOKMARKED: bool | None, PUBLIC: bool | None, SEQUENCE: int | None,
							TYPE: int | None, QUERY: str | None, OFFSET: int | None, 
							SIZE: int | None, FILTERS: List[dict] | None, 
							SORT_FIELDS: List[dict] | None, 
							SEARCH_RESULT_FIELDS: List[dict] | None,
							SIMILAR_ASSET_ID: str | None, MIN_SCORE: float | None, 
							EXCLUDE_TOTAL_RECORD_COUNT: bool | None, 
							FILTER_BINDER: str | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start update saved search", sep=" ")
			
			SAVED_SEARCH_INFO = _update_saved_search(self.token, self.config["serviceApiUrl"], 
				ID, NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, TYPE, QUERY, OFFSET, SIZE, FILTERS, 
				SORT_FIELDS, SEARCH_RESULT_FIELDS, SIMILAR_ASSET_ID, MIN_SCORE, 
				EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Update saved search complete", sep=" ")

			return SAVED_SEARCH_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Update saved search failed", sep=" ")
			raise Exception(error.args[0])						

	# Video Tracking
	"""
	Description:
	Gets video tracking.
	Parameters:
	ASSET_ID (str): The id of the asset.
	TRACKING_EVENT (str): The tracking event of the asset. The value of tracking 
    event's value can be 0-5 with 0 being no tracking event, 1-4 being the progress in quarters, 
    i.e 3 meaning it is tracking 3 quarters of the video, and 5 meaning that the tracking is 
	hidden.
	SECONDS (int | None): The seconds into the video being tracked.
	Returns:
	dict: The information of the video tracking.
	Exception: If the API type is not portal.
	Exception: If get video tracking fails.
	"""
	def get_video_tracking(self, ASSET_ID: str, TRACKING_EVENT: str,
						   SECONDS: int | None) -> dict:
		try:
			if self.config["apiType"] != "portal":
				raise Exception("This function is only available for portal API type.")
			
			print(datetime.now().strftime('%H:%M:%S'), "Start get video tracking", sep=" ")

			VIDEO_TRACKING_INFO = _get_video_tracking(self.token, self.config["serviceApiUrl"], 
				ASSET_ID, TRACKING_EVENT, SECONDS, self.debug_mode)
			
			print(datetime.now().strftime('%H:%M:%S'), "Get video tracking complete", sep=" ")

			return VIDEO_TRACKING_INFO
		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Get video tracking failed", sep=" ")
			raise Exception(error.args[0])

	"""
	Description:
	Calls any nomad function given URL, method, and body.
	Parameters:
	URL_PATH (str): The URL of the nomad function.
	METHOD (str): The method of the nomad function.
	BODY (dict): The body of the nomad function.
	NOT_API_PATH (bool): If the path has /api in it.
	Returns:
	dict: The information of the nomad function.
	Exception: If misc function fails.
	"""
	def misc_function(self, URL_PATH: str, METHOD: str, BODY: dict, NOT_API_PATH: bool) -> dict: 
		try:
			print(datetime.now().strftime('%H:%M:%S'), f"Calling function {URL_PATH}: ", sep=" ")

			API_URL = f'{self.config["serviceApiUrl"]}/{URL_PATH}'
			if NOT_API_PATH:
				API_URL = API_URL.replace('/api', '')
				API_URL = API_URL.replace('app-api.', '')
				API_URL = API_URL.replace('admin-app.', '')

			HEADERS = {
				'Authorization': f'Bearer {self.token}',
				'Content-Type': 'application/json'
			}

			if self.debug_mode:
				print(f"API URL: {API_URL}\nMETHOD: {METHOD}\nBODY: {json.dumps(BODY, indent=4)}")

			if BODY:
				REQUEST = requests.request(METHOD, API_URL, headers=HEADERS, json=BODY)
			else:
				REQUEST = requests.request(METHOD, API_URL, headers=HEADERS)

			print(datetime.now().strftime('%H:%M:%S'), f"Function {URL_PATH} complete", sep=" ")

			return REQUEST.json()

		except Exception as error:
			print(datetime.now().strftime('%H:%M:%S'), "Misc function failed", sep=" ")
			raise Exception(error.args[0])
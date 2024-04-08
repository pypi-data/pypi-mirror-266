const Url = "/api/v1";

export const API_Path = {
  applianceDescriptionUrl: Url + "/appliance/description",
  applianceIndexUrl: Url + "/appliance/index",
  applianceReindexUrl: Url + "/appliance/reindex",

  userProfileUrl: Url + "/user/profile",

  agentAskStreamedBaseUrl: Url + "/agent/ask-streamed",
  agentConversationsGetUrl: (shortcode) =>
    Url + "/agent/conversations/" + shortcode,

  conversationsGetUrl: (guid) => Url + "/conversations/" + guid,
  conversationsDeleteUrl: (guid) => Url + "/conversations/" + guid,

  collectionsGetUrl: Url + "/collections",
  collectionsAddUrl: Url + "/collections",
  collectionsGetCollectionUrl: (shortcode) => Url + "/collections/" + shortcode,
  collectionsDeleteCollectionUrl: (shortcode) =>
    Url + "/collections/" + shortcode,
  collectionsUploadFilesUrl: (shortcode) =>
    Url + "/collections/upload_files/" + shortcode,
  collectionsDownloadFileUrl: (shortcode, file_guid) =>
    // Url + "/collections/" + shortcode + "/" + file_guid + "/text",
    Url + "/collections/" + shortcode + "/" + file_guid,
};

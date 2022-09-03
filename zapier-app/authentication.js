// basic Bearer token authentication
module.exports = {
    type: "custom",
    test: {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: "Bearer {{bundle.authData.api_key}}",
      },
      url: "{{process.env.BASE_API_URL}}/zapier/auth/",
    },
    fields: [
      {
        key: "api_key",
        label: "Personal API key",
        helpText: "Your API key is available from your YunoJuno account.",
        required: true,
      },
    ],
    customConfig: {},
  };

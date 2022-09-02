module.exports = {
  type: 'custom',
  test: {
    headers: { 'Authorization': 'Bearer {{bundle.authData.api_key}}' },
    url: '{{process.env.BASE_API_URL}}/zapier/auth/',
  },
  fields: [{ computed: false, key: 'api_key', required: true }],
  customConfig: {},
};

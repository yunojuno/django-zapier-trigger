module.exports = {
  type: 'custom',
  test: {
    headers: { 'X-API-KEY': '{{bundle.authData.api_key}}' },
    params: { api_key: '{{bundle.authData.api_key}}' },
    url: '{{process.env.BASE_API_URL}}',
  },
  fields: [{ computed: false, key: 'api_key', required: true }],
  customConfig: {},
};

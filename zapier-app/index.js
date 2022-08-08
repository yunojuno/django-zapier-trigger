const authentication = require('./authentication');
const newBookTrigger = require('./triggers/new_book.js');

module.exports = {
  version: require('./package.json').version,
  platformVersion: require('zapier-platform-core').version,
  authentication: authentication,
  triggers: { [newBookTrigger.key]: newBookTrigger },
};

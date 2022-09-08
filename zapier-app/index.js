const authentication = require("./authentication");
const newBook = require("./triggers/new_book.js");
const newFilms = require("./triggers/new_films.js");

module.exports = {
    version: require("./package.json").version,
    platformVersion: require("zapier-platform-core").version,
    authentication: authentication,
    triggers: { [newBook.key]: newBook, [newFilms.key]: newFilms }
};

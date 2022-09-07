const authentication = require("./authentication");
const newBook = require("./triggers/new_book.js");
const newBooks = require("./triggers/new_books.js");

module.exports = {
    version: require("./package.json").version,
    platformVersion: require("zapier-platform-core").version,
    authentication: authentication,
    requestTemplate: {
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${bundle.authData.api_key}`
        }
    },
    triggers: { [newBook.key]: newBook, [newBooks.key]: newBooks }
};

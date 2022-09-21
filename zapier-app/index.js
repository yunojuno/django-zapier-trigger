const authentication = require("./authentication");
const newBook = require("./triggers/new_book.js");
const newFilm = require("./triggers/new_film.js");

const setRequestHeaders = (request, z, bundle) => {
    request.headers["Content-Type"] = "application/json";
    request.headers["Accept"] = "application/json";
    request.headers["Authorization"] = `Token ${bundle.authData.api_key}`;
    return request;
};

module.exports = {
    version: require("./package.json").version,
    platformVersion: require("zapier-platform-core").version,
    authentication: authentication.apiKeyAuthentication,
    beforeRequest: [setRequestHeaders],
    triggers: { [newBook.key]: newBook, [newFilm.key]: newFilm }
};
